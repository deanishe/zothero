# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Search index database."""

from __future__ import print_function, absolute_import

from contextlib import contextmanager
from datetime import datetime
import logging
import os
import sqlite3
import struct

from .util import dt2sqlite, timed, time_since, shortpath
from .zotero import Entry

# Version of the database schema/data format.
DB_VERSION = 2

# SQL schema for the search database. The Entry is also stored in the
# database as JSON for speed (it takes 7 SQL queries to retrieve an
# Entry from the Zotero database).
INDEX_SCHEMA = """
CREATE VIRTUAL TABLE search USING fts3(
    key, title, year, creators,
    tags, collections, attachments, notes
);

CREATE TABLE modified (
    key TEXT PRIMARY KEY NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE data (
    key TEXT PRIMARY KEY NOT NULL,
    json TEXT DEFAULT "{}"
);

CREATE TABLE dbinfo (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
)
"""

log = logging.getLogger(__name__)

SEARCH_SQL = """
SELECT search.key AS key, json, rank(matchinfo(search)) AS score
FROM search
LEFT JOIN data ON search.key = data.key
WHERE search MATCH ?
ORDER BY score DESC
LIMIT 100
"""

RESET_SQL = u"""
DROP TABLE IF EXISTS `data`;
DROP TABLE IF EXISTS `dbinfo`;
DROP TABLE IF EXISTS `modified`;
DROP TABLE IF EXISTS `search`;
VACUUM;
PRAGMA INTEGRITY_CHECK;
"""

# Search database column names
COLUMNS = ('title', 'year', 'creators', 'tags',
           'collections', 'attachments', 'notes')

# Search weightings for columns. The first column (key) is ignored (0.0)
# collections, attachments and notes have slightly lower weightings.
WEIGHTINGS = (0.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.7)


class InitialiseDB(Exception):
    """Raised if database needs initialising."""


def make_rank_func(weights):
        """Search ranking function.

        Use floats (1.0 not 1) for more accurate results. Use 0 to ignore a
        column.

        Adapted from <http://goo.gl/4QXj25> and <http://goo.gl/fWg25i>

        :param weights: list or tuple of the relative ranking per column.
        :type weights: :class:`tuple` OR :class:`list`
        :returns: a function to rank SQLITE FTS results
        :rtype: :class:`function`

        """
        def rank(matchinfo):
            """
            `matchinfo` is defined as returning 32-bit unsigned integers in
            machine byte order (see http://www.sqlite.org/fts3.html#matchinfo)
            and `struct` defaults to machine byte order.
            """
            bufsize = len(matchinfo)  # Length in bytes.
            matchinfo = [struct.unpack(b'I', matchinfo[i:i + 4])[0]
                         for i in range(0, bufsize, 4)]
            it = iter(matchinfo[2:])
            return sum(x[0] * w / x[1]
                       for x, w in zip(zip(it, it, it), weights)
                       if x[1])

        return rank


class Index(object):
    """Search index database."""

    def __init__(self, dbpath):
        self.dbpath = dbpath
        self._conn = None

    @property
    def conn(self):
        """Connection to the database."""
        if not self._conn:
            conn = sqlite3.connect(self.dbpath)
            conn.row_factory = sqlite3.Row

            if not self._db_valid(conn):
                log.debug('[index] initialising %r ...', shortpath(self.dbpath))
                conn.executescript(INDEX_SCHEMA)
                with conn as c:
                    sql = u"""
                        INSERT INTO dbinfo VALUES('version', ?)
                    """
                    c.execute(sql, (str(DB_VERSION),))

            log.debug('[index] opened %r', shortpath(self.dbpath))
            conn.create_function('rank', 1, make_rank_func(WEIGHTINGS))
            self._conn = conn

        return self._conn

    def _db_valid(self, conn):
        """Validate database version against `DB_VERSION`."""
        sql = u"""
            SELECT `value` AS `version`
                FROM `dbinfo`
            WHERE `key` = 'version'
        """
        try:
            row = conn.execute(sql).fetchone()
        except sqlite3.OperationalError:
            return False

        if int(row['version']) != DB_VERSION:  # index must be rebuilt
            log.debug('[index] clearing stale database %r ...',
                      shortpath(self.dbpath))

            with conn as c:
                c.executescript(RESET_SQL)
            return False

        return True

    @contextmanager
    def cursor(self):
        """Context manager providing database cursor."""
        with self.conn as c:
            yield c.cursor()

    @property
    def empty(self):
        """Return ``True`` if index database is empty."""
        with self.conn as c:
            row = c.execute('SELECT COUNT(*) AS n FROM search').fetchone()
            return row['n'] == 0

    @property
    def last_updated(self):
        """Return modified time of database file."""
        if not os.path.exists(self.dbpath):
            log.debug('[index] not yet initialised')
            return 0.0

        t = os.path.getmtime(self.dbpath)
        log.debug('[index] last updated %s', time_since(t))
        return t

    def entry(self, key):
        """Return `Entry` for `key`.

        Args:
            key (str): Zotero database key

        Returns:
            zothero.zotero.Entry: `Entry` for `key` or `None` if not found.
        """
        sql = """SELECT json FROM data WHERE key = ?"""
        row = self.conn.execute(sql, (key,)).fetchone()
        if not row:
            return None

        return Entry.from_json(row['json'])

    def search(self, query):
        """Search index for ``query``.

        Args:
            query (unicode): Query to search for

        Returns:
            list: `Entry` objects for matching database items.
        """
        entries = []
        for row in self.conn.execute(SEARCH_SQL, (query,)):
            entries.append(Entry.from_json(row['json']))

        # If we didn't get many results, perform a second search using
        # a wildcard
        if len(entries) < 30 and not query.endswith('*'):
            seen = {e.key for e in entries}  # ignore any duplicates

            for row in self.conn.execute(SEARCH_SQL, (query + '*',)):
                if row['key'] not in seen:
                    entries.append(Entry.from_json(row['json']))

        log.info('[index] %d result(s) for %r', len(entries), query)
        return entries

    def update(self, zot):
        """Update search index from a `Zotero` instance.

        If the Zotero database is newer than the index (or the index
        is empty), retrieve all entries from the Zotero DB and add them
        to the index.

        Args:
            zot (zothero.zotero.Zotero): `Zotero` object whose items
                should be added to the search index.

        Returns:
            boolean: ``True`` if index was updated, else ``False``
        """
        # Only update search index if Zotero database is newer or
        # the index hasn't been filled yet.
        if zot.last_updated <= self.last_updated and not self.empty:
            log.debug('[index] up to date: %r', shortpath(self.dbpath))
            return False

        with timed('updated search index'):
            log.debug('[index] updating %r ...', shortpath(self.dbpath))

            with self.cursor() as c:
                # ------------------------------------------------------
                # Get keys of indexed items
                sql = u'SELECT key FROM data'
                ikeys = {row['key'] for row in c.execute(sql)}

                # ------------------------------------------------------
                # New and updated entries

                i = j = 0  # updated, new entries
                if not ikeys:  # Index is empty, fetch all entries
                    it = zot.all_entries()
                else:  # Only fetch entries modified since last update
                    # Zotero stores TIMESTAMPs in UTC
                    dt = datetime.utcfromtimestamp(self.last_updated)
                    it = zot.modified_since(dt)

                for e in it:

                    data = [
                        e.key,
                        e.title,
                        unicode(e.year),
                        u' '.join([d.family for d in e.creators]),
                        u' '.join(e.tags),
                        u' '.join([d.name for d in e.collections]),
                        u' '.join([d.name for d in e.attachments]),
                        u' '.join(e.notes),
                    ]

                    if e.key in ikeys:  # update
                        i += 1
                        # Fulltext search
                        sql = u"""
                            UPDATE search
                                SET title = ?, year = ?, creators = ?,
                                    tags = ?, collections = ?,
                                    attachments = ?, notes = ?
                            WHERE key = ?
                        """
                        c.execute(sql, data[1:] + [e.key])

                        # JSON data
                        sql = u'UPDATE data SET json = ? WHERE key = ?'
                        c.execute(sql, (e.json(), e.key))

                        # Modified time
                        sql = u'UPDATE modified SET modified = ? WHERE key = ?'
                        c.execute(sql, (dt2sqlite(e.modified), e.key))

                    else:  # new entry
                        j += 1
                        # Fulltext search table
                        sql = u"""
                            INSERT INTO search VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        c.execute(sql, data)

                        # JSON data
                        c.execute('INSERT INTO data VALUES (?, ?)',
                                  (e.key, e.json()))

                        # Modified time
                        c.execute('INSERT INTO modified VALUES (?, ?)',
                                  (e.key, dt2sqlite(e.modified)))

                # ------------------------------------------------------
                # Remove deleted entries from index
                gone = ikeys - set(zot.keys())

                queries = (
                    u'DELETE FROM search WHERE key = ?',
                    u'DELETE FROM data WHERE key = ?',
                    u'DELETE FROM modified WHERE key = ?',
                )
                for sql in queries:
                    c.executemany(sql, [(key,) for key in gone])

                log.debug('[index] %d updated, %d new, %d deleted entries',
                          i, j, len(gone))

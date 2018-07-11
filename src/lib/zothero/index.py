# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Search index based on SQLite."""

from __future__ import print_function, absolute_import

from contextlib import contextmanager
from datetime import datetime
import logging
import os
import sqlite3
import struct
from urlparse import urlparse

from .util import dt2sqlite, timed, time_since, shortpath
from .zotero import Entry

# Version of the database schema/data format.
# Increment this every time the schema or JSON format changes to
# invalidate the existing cache.
DB_VERSION = 7

# SQL schema for the search database. The Entry is also stored in the
# database as JSON for speed (it takes 7 SQL queries to retrieve an
# Entry from the Zotero database).
INDEX_SCHEMA = """
CREATE VIRTUAL TABLE search USING fts3(
    id, title, year, creators, authors, editors,
    tags, collections, attachments, notes, abstract, all
);

CREATE TABLE modified (
    id INTEGER PRIMARY KEY NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE data (
    id INTEGER PRIMARY KEY NOT NULL,
    json TEXT DEFAULT "{}"
);

CREATE TABLE dbinfo (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
)
"""

log = logging.getLogger(__name__)

SEARCH_SQL = """
SELECT search.id AS id, json, rank(matchinfo(search)) AS score
FROM search
LEFT JOIN data ON search.id = data.id
WHERE search MATCH ?
ORDER BY score DESC
LIMIT 100
"""

RESET_SQL = """
DROP TABLE IF EXISTS `data`;
DROP TABLE IF EXISTS `dbinfo`;
DROP TABLE IF EXISTS `modified`;
DROP TABLE IF EXISTS `search`;
VACUUM;
PRAGMA INTEGRITY_CHECK;
"""

# Search database column names
COLUMNS = ('title', 'year', 'creators', 'authors', 'editors', 'tags',
           'collections', 'attachments', 'notes', 'abstract', 'all')

# Search weightings for columns. The first column (key) is ignored (0.0)
# collections, attachments, notes, abstract and all have lower weightings.
# "all" is particularly low-ranked to avoid polluting results
WEIGHTINGS = (0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.4, 0.3, 0.3, 0.1)


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
            """Rank function for SQLite.

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
        """Create a new search index.

        Args:
            dbpath (str): Path to SQLite database file.

        """
        self.dbpath = dbpath
        self._conn = None

    @property
    def conn(self):
        """Return connection to the database."""
        if not self._conn:
            conn = sqlite3.connect(self.dbpath)
            conn.row_factory = sqlite3.Row

            if not self._db_valid(conn):
                log.debug('[index] initialising %r ...',
                          shortpath(self.dbpath))

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

    def entry(self, entry_id):
        """Return `Entry` for `entry_id`.

        Args:
            id (int): Zotero database ID

        Returns:
            zothero.zotero.Entry: `Entry` for `id` or `None` if not found.

        """
        sql = """SELECT json FROM data WHERE id = ?"""
        row = self.conn.execute(sql, (entry_id,)).fetchone()
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
            seen = {e.id for e in entries}  # ignore any duplicates

            for row in self.conn.execute(SEARCH_SQL, (query + '*',)):
                if row['id'] not in seen:
                    entries.append(Entry.from_json(row['json']))

        log.info('[index] %d result(s) for %r', len(entries), query)
        return entries

    def update(self, zot, force=False):
        """Update search index from a `Zotero` instance.

        If the Zotero database is newer than the index (or the index
        is empty), retrieve entries from the Zotero DB and add them
        to the index.

        Attempts to only load modified entries, but if there are none,
        and the database file has changed, forces a full reload.

        Args:
            zot (zotero.Zotero): `Zotero` object whose items
                should be added to the search index.
            force (bool, optional): Re-index all entries, not just
                modified ones.

        Returns:
            boolean: ``True`` if index was updated, else ``False``

        """
        # Only update search index if Zotero database is newer or
        # the index hasn't been populated yet.
        if zot.last_updated <= self.last_updated and not self.empty:
            log.debug('[index] up to date: %r', shortpath(self.dbpath))
            return False

        with timed('updated search index'):
            # First try to only update entries whose modified date (or
            # whose attachments' modified date) has changed.
            if not self._update(zot, force):
                # Index wasn't updated, although the database has
                # changed. That means a note or something else that
                # doesn't have a modified date was changed.
                # Force a full update.
                self._update(zot, True)

        return True

    def _update(self, zot, force=False):
        """Update search index from a `Zotero` instance.

        Retrieve Zotero entries and add to/update in the search index.

        Args:
            zot (zotero.Zotero): `Zotero` object whose items
                should be added to the search index.
            force (bool, optional): Re-index all entries, not just
                modified ones.

        Returns:
            boolean: ``True`` if index was updated, else ``False``

        """
        log.debug('[index] updating %r ...', shortpath(self.dbpath))
        if force:
            log.debug('[index] forcing full re-index ...')

        with self.cursor() as c:
            # ------------------------------------------------------
            # Get keys of indexed items
            sql = u'SELECT id FROM data'
            index_ids = {row['id'] for row in c.execute(sql)}

            # ------------------------------------------------------
            # New and updated entries

            i = j = 0  # updated, new entries
            if force or not index_ids:  # Index is empty, fetch all entries
                it = zot.all_entries()
            else:  # Only fetch entries modified since last update
                # Zotero stores TIMESTAMPs in UTC
                dt = datetime.utcfromtimestamp(self.last_updated)
                it = zot.modified_since(dt)

            # fields in zdata to exclude from all_
            zfields_ignore = ('title', 'numPages', 'numberOfVolumes')

            for e in it:

                tags = u' '.join(e.tags)
                collections = u' '.join([d.name for d in e.collections])
                attachments = u' '.join([d.name for d in e.attachments
                                         if d.name])
                notes = u' '.join(e.notes)

                names = {d.family for d in e.creators + e.authors + e.editors
                         if d.family}

                all_ = [e.title, u' '.join(names), tags, collections,
                        attachments, notes, e.abstract, unicode(e.year),
                        e.date]

                for k, v in e.zdata.items():
                    if k in zfields_ignore or 'date' in k.lower() or not v:
                        continue

                    if k == 'url':
                        hostname = urlparse(v).hostname
                        if not hostname:
                            continue

                        if hostname.startswith('www.'):
                            hostname = hostname[4:]
                        all_.append(hostname)
                    else:
                        all_.append(v)

                all_ = [v for v in all_ if v]

                data = [
                    e.id,
                    e.title,
                    unicode(e.year),
                    u' '.join([d.family for d in e.creators if d.family]),
                    u' '.join([d.family for d in e.authors if d.family]),
                    u' '.join([d.family for d in e.editors if d.family]),
                    tags,
                    collections,
                    attachments,
                    notes,
                    e.abstract,
                    u' '.join(all_),
                ]

                if e.id in index_ids:  # update
                    i += 1
                    # Fulltext search
                    sql = u"""
                        UPDATE search
                            SET title = ?, year = ?, creators = ?,
                                authors = ?, editors = ?,
                                tags = ?, collections = ?,
                                attachments = ?, notes = ?,
                                abstract = ?, all = ?
                        WHERE id = ?
                    """
                    c.execute(sql, data[1:] + [e.id])

                    # JSON data
                    sql = u'UPDATE data SET json = ? WHERE id = ?'
                    c.execute(sql, (e.json(), e.id))

                    # Modified time
                    sql = u'UPDATE modified SET modified = ? WHERE id = ?'
                    c.execute(sql, (dt2sqlite(e.modified), e.id))

                else:  # new entry
                    j += 1
                    # Fulltext search table
                    sql = u"""
                        INSERT INTO search
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    c.execute(sql, data)

                    # JSON data
                    c.execute('INSERT INTO data VALUES (?, ?)',
                              (e.id, e.json()))

                    # Modified time
                    c.execute('INSERT INTO modified VALUES (?, ?)',
                              (e.id, dt2sqlite(e.modified)))

            # ------------------------------------------------------
            # Remove deleted entries from index
            gone = index_ids - set(zot.ids())

            queries = (
                u'DELETE FROM search WHERE id = ?',
                u'DELETE FROM data WHERE id = ?',
                u'DELETE FROM modified WHERE id = ?',
            )
            for sql in queries:
                c.executemany(sql, [(id_,) for id_ in gone])

            log.debug('[index] %d updated, %d new, %d deleted entries',
                      i, j, len(gone))

        # Return ``True`` if index was updated
        return (len(gone) + i + j) > 0

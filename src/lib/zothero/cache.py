# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-11-13
#

"""Simple key-value store based on sqlite3.

Data is stored via `Store` sub-objects assigned to each table.
"""

from __future__ import print_function, absolute_import


from contextlib import contextmanager
import logging
import os
import re
import sqlite3
import time


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Create a new database
SQL_SCHEMA = u"""
CREATE TABLE `dbinfo` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    `version` INTEGER NOT NULL
);

INSERT INTO `dbinfo` VALUES (1, 1);
"""

# Add a new table
SQL_TABLE = u"""

CREATE TABLE `{name}` (
    `key` TEXT PRIMARY KEY,
    `value` BLOB NOT NULL,
    `updated` INTEGER DEFAULT 0
);

"""

# Convenience constants; currently unused
FOREVER = 0
ONE_MINUTE = 60
ONE_HOUR = 3600
ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7
ONE_YEAR = ONE_DAY * 365
TWO_YEARS = ONE_YEAR * 2
THREE_YEARS = ONE_YEAR * 3


def _nullop(value):
    """Do-nothing handler. Simply returns ``value``."""
    return value


class Store(object):
    """Key-value store based on an sqlite3 table.

    Instantiate these via `Cache.open(name)`.

    Attributes:
        cache (Cache): `Cache` object holding this store's database.
        convert_in (callable): Called on input before storage.
        convert_out (callable): Called on output before returning it.
        name (str): Name of store (and database table).
    """
    def __init__(self, name, cache, convert_in=None, convert_out=None):
        """Create new `Store`.

        Args:
            name (str): Name of store (and database table).
            cache (Cache): `Cache` object managing the database.
            convert_in (callable, optional): Called on input before storage.
            convert_out (callable, optional): Called on output before return.
        """
        self.name = name
        self.cache = cache
        self.convert_in = convert_in or _nullop
        self.convert_out = convert_out or _nullop

    @property
    def conn(self):
        """Database connection."""
        return self.cache.conn

    @contextmanager
    def cursor(self):
        """Context manager providing database cursor."""
        with self.conn as c:
            yield c.cursor()

    def keys(self):
        """Iterate over all store keys.

        Yields:
            unicode: Store keys.
        """
        sql = u"""
            SELECT `key` FROM `{table}` WHERE 1
        """.format(table=self.name)

        for row in self.conn.execute(sql):
            yield row['key']

    def get(self, key, default=None):
        """Return value for `key` or `default`.

        Passes result through `self.convert_out()` before returning.

        Args:
            key (str): Database key.
            default (obj, optional): What to return if `key` is absent.

        Returns:
            obj: Object deserialised from the database.
        """
        key = self._validate_key(key)
        sql = u"""
            SELECT `value` FROM `{table}` WHERE key = ?
        """.format(table=self.name)

        r = self.conn.execute(sql, (key,)).fetchone()

        if r:
            return self.convert_out(r['value'])

        return default

    def set(self, key, value):
        """Set value for key, passing `value` through `self.convert_in()`.

        Args:
            key (str): Database key.
            value (obj): Object to store in database.
        """
        key = self._validate_key(key)
        value = self.convert_in(value)

        with self.cursor() as c:
            sql = u"""
                UPDATE `{table}`
                    SET `value` = ?, `updated` = ?
                    WHERE key = ?
            """.format(table=self.name)

            c.execute(sql, (value, time.time(), key))

            if c.rowcount > 0:
                log.debug(u'[%s] updated `%s` -> %r', self.name, key, value)
                return

        with self.cursor() as c:
            sql = u"""
                INSERT INTO `{table}`
                    (`key`, `value`, `updated`)
                    VALUES (?, ?, ?)
            """.format(table=self.name)

            c.execute(sql, (key, value, time.time()))

            if c.rowcount > 0:
                log.debug(u'[%s] inserted `%s` -> %r', self.name, key, value)
                return

        log.error("[%s] couldn't save value for key %r", self.name, key)

    def delete(self, key):
        """Remove item from store."""
        sql = u"""
            DELETE FROM `{table}` WHERE `key` = ?
        """.format(table=self.name)

        with self.cursor() as c:
            c.execute(sql, (key,))

            if c.rowcount:
                return True

        return False

    def updated(self, key=None):
        """Timestamp of last time ``key`` was updated.

        Args:
            key (unicode, optional): Key of item to query. If no key
                is specified, returns the last time any entry was
                updated.

        Returns:
            float: UNIX timestamp of last update, or ``0.0`` if key
                doesn't exit.
        """
        if key:
            sql = u"""
                SELECT `updated` FROM `{table}` WHERE `key` = ?
            """.format(table=self.name)

            row = self.conn.execute(sql, (key,)).fetchone()
            if row:
                return row['updated']

            return 0.0

        # Return latest updated
        sql = u"""
            SELECT MAX(`updated`) AS `updated` FROM `{table}`
        """.format(table=self.name)

        row = self.conn.execute(sql).fetchone()
        return row['updated'] if row['updated'] else 0.0

    def _validate_key(self, key):
        """Coerce `key` to Unicode or raise `ValueError`.

        Args:
            key (str or unicode): String key.

        Raises:
            TypeError: Raised if `key` isn't a string.

        Returns:
            unicode: Unicode `key`.
        """
        if isinstance(key, str):
            key = unicode(key, 'utf-8')
        elif not isinstance(key, unicode):
            raise TypeError(
                "`key` must be `str` or `unicode`, not `{}`".format(
                    key.__class__.__name__)
            )
        return key


class Cache(object):
    """Key-value store manager.

    Attributes:
        filepath (str): Path to cache sqlite file.
        invalid_names (tuple): Names not permitted for Stores
            (i.e. bad table names).
    """

    invalid_names = ('dbinfo', 'sqlite_sequence', 'sqlite_master')

    def __init__(self, filepath):
        """Open/create and open cache at `filepath`.

        Args:
            filepath (str): Path of cache sqlite database.
        """
        self.filepath = filepath
        self._conn = None
        self.conn

    @property
    def conn(self):
        """Connection to database."""
        if not self._conn:
            conn = sqlite3.connect(self.filepath)
            conn.row_factory = sqlite3.Row
            with conn as c:
                try:
                    c.execute(u'SELECT * FROM `dbinfo`')
                except sqlite3.OperationalError:
                    log.debug('[cache] initialising %r...', self.filepath)
                    c.executescript(SQL_SCHEMA)

            self._conn = conn

        return self._conn

    @contextmanager
    def cursor(self):
        """Context manager providing database cursor."""
        with self.conn as c:
            yield c.cursor()

    def open(self, name, convert_in=None, convert_out=None):
        """Open a `Store` with `name` and using the specified converters.

        Args:
            name (str): The name of the Store/database table.
            convert_in (callable, optional): Serialise database values.
            convert_out (callable, optional): Deserialise database values.

        Returns:
            Store: `Store` object.
        """
        # log.debug('self.caches=%r', self.caches)
        log.debug('[cache] opening store %r...', name)
        if name not in self.caches:
            log.info('[cache] creating table `%s`...', name)
            self._add_table(name)

        return Store(name, self, convert_in, convert_out)

    def clear(self, name=None):
        """Clear Stores.

        If no `name` is specified, the entire cache is deleted.

        Args:
            name (str, optional): Name of a specific store.

        Raises:
            ValueError: Raised if specified Store does not exit.
        """
        if name is None:  # Delete whole cache
            try:
                os.unlink(self.filepath)
            except OSError:
                pass
            return
        elif name in self.caches:
            sql = u'DROP TABLE `{}`'.format(name)
            with self.conn as c:
                c.execute(sql)
                return
        else:
            raise ValueError('store not found : {!r}'.format(name))

    @property
    def caches(self):
        """Synonym for `stores`."""
        return self.stores

    @property
    def stores(self):
        """List of Stores in this Cache.

        Returns:
            list: String names of Stores.
        """
        sql = u"SELECT name FROM `sqlite_master` WHERE type='table'"
        rows = self.conn.execute(sql)
        return [r['name'] for r in rows
                if r['name'] not in self.invalid_names]

    def _add_table(self, name):
        """Add new table to database, verifying name first.

        Name should contain only lowercase ASCII letters, digits and
        underscore (_). May not start with a digit.

        Args:
            name (str): Name of the table.

        Raises:
            ValueError: Raised if `name` is not permitted.
        """
        if name.lower() in self.invalid_names:
            raise ValueError('name is reserved: %r' % name.lower())
        if not name or \
                not re.match(r'[a-z][a-z0-9_]+', name) \
                or len(name) > 100:

            raise ValueError(
                'invalid name: %r. Name must be 1-100 characters, '
                'a-z and _ only.' % name.lower()
            )

        sql = SQL_TABLE.format(name=name)
        with self.conn as c:
            c.executescript(sql)

        log.debug(u'[cache] added table `%s`', name)
        log.debug(u'self.caches=%r', self.caches)

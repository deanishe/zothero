# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Interface to the Zotero database.

All data classes are based on ``AttrDict``, which means their data
can be accesses either as ``dict`` values or as attributes, i.e.
``Entry.title`` and ``Entry['title']`` are equivalent.

The `Zotero` class is a fairly-thin wrapper around the SQLite database
stored by Zotero. It abstracts away the implementation details of the
Zotero datastore.
"""

from __future__ import print_function, absolute_import

import logging
import os
import sqlite3

from . import csl

from .models import (
    Entry,
    Attachment,
    Collection,
    Creator,
)

from .util import (
    dt2sqlite,
    HTMLText,
    parse_date,
    shortpath,
    sqlite2dt,
    time_since,
)


log = logging.getLogger(__name__)

# Accepted extensions for attachments
# ATTACHMENT_EXTS = {
#     '.doc',
#     '.docx',
#     '.epub',
#     '.pdf',
# }


ITEMS_SQL = u"""
SELECT  items.itemID AS id,
        items.dateModified AS modified,
        items.key AS key,
        items.libraryID AS library,
        itemTypes.typeName AS type
    FROM items
    LEFT JOIN itemTypes
        ON items.itemTypeID = itemTypes.itemTypeID
    LEFT JOIN deletedItems
        ON items.itemID = deletedItems.itemID
-- Ignore notes, webpages and attachments
WHERE items.itemTypeID not IN (1, 13, 14)
AND deletedItems.dateDeleted IS NULL
"""

CREATORS_SQL = u"""
SELECT  creators.firstName AS given,
        creators.lastName AS family,
        itemCreators.orderIndex AS `index`,
        creatorTypes.creatorType AS `type`
    FROM creators
    LEFT JOIN itemCreators
        ON creators.creatorID = itemCreators.creatorID
    LEFT JOIN creatorTypes
        ON itemCreators.creatorTypeID = creatorTypes.creatorTypeID
WHERE itemCreators.itemID = ?
ORDER BY `index` ASC
"""

COLLECTIONS_SQL = u"""
SELECT  collections.collectionName AS name,
        collections.key AS key
    FROM collections
    LEFT JOIN collectionItems
        ON collections.collectionID = collectionItems.collectionID
WHERE collectionItems.itemID = ?
"""

# ATTACHMENTS_SQL = u"""
# SELECT  itemAttachments.path AS path,
#         items.key AS key
#     FROM itemAttachments
#     LEFT JOIN items
#         ON itemAttachments.itemID = items.itemID
# WHERE itemAttachments.parentItemID = ?
# """

ATTACHMENTS_SQL = u"""
SELECT
    items.key AS key,
    itemAttachments.path AS path,
    (SELECT  itemDataValues.value
        FROM itemData
        LEFT JOIN fields
            ON itemData.fieldID = fields.fieldID
        LEFT JOIN itemDataValues
            ON itemData.valueID = itemDataValues.valueID
    WHERE itemData.itemID = items.itemID AND fields.fieldName = 'title')
    title,
    (SELECT  itemDataValues.value
        FROM itemData
        LEFT JOIN fields
            ON itemData.fieldID = fields.fieldID
        LEFT JOIN itemDataValues
            ON itemData.valueID = itemDataValues.valueID
    WHERE itemData.itemID = items.itemID AND fields.fieldName = 'url')
    url
FROM itemAttachments
    LEFT JOIN items
        ON itemAttachments.itemID = items.itemID
WHERE itemAttachments.parentItemID = ?
"""

METADATA_SQL = u"""
SELECT  fields.fieldName AS name,
        itemDataValues.value AS value
    FROM itemData
    LEFT JOIN fields
        ON itemData.fieldID = fields.fieldID
    LEFT JOIN itemDataValues
        ON itemData.valueID = itemDataValues.valueID
WHERE itemData.itemID = ?
"""

NOTES_SQL = u"""
SELECT itemNotes.note AS note
    FROM itemNotes
    LEFT JOIN items
        ON itemNotes.itemID = items.itemID
WHERE itemNotes.parentItemID = ?
"""

TAGS_SQL = u"""
SELECT tags.name AS name
    FROM tags
    LEFT JOIN itemTags
        ON tags.tagID = itemTags.tagID
WHERE itemTags.itemID = ?
"""


class Zotero(object):
    """Interface to the Zotero database."""

    def __init__(self, datadir, dbpath=None):
        """Load Zotero data from ``datadir``.

        Args:
            datadir (str): Path to Zotero's data directory.
            dbpath (str, optional): Path to `zotero.sqlite` if not in
                ``datadir``.
        """
        self.datadir = datadir
        self.dbpath = dbpath or os.path.join(datadir, 'zotero.sqlite')
        self._conn = None

    @property
    def conn(self):
        """Connection to the database."""
        if not self._conn:
            self._conn = sqlite3.connect(self.dbpath)
            self._conn.row_factory = sqlite3.Row
            log.debug('[zotero] opened database %r', shortpath(self.dbpath))

        return self._conn

    @property
    def last_updated(self):
        """Return modified time of database file."""
        t = os.path.getmtime(self.dbpath)
        log.debug('[zotero] database last modified %s', time_since(t))
        return t

    @property
    def storage_dir(self):
        """Path to Zotero's internal directory for attachments."""
        path = os.path.join(self.datadir, 'storage')
        if not os.path.exists(path):
            raise ValueError('storage directory does not exist: %r' % path)

        return path

    @property
    def styles_dir(self):
        """Path to Zotero's directory for styles."""
        path = os.path.join(self.datadir, 'styles')
        if not os.path.exists(path):
            raise ValueError('styles directory does not exist: %r' % path)

        return path

    def keys(self):
        """Iterate entry keys."""
        for row in self.conn.execute(ITEMS_SQL):
            yield row['key']

    def entry(self, key):
        """Return Entry for key."""
        sql = ITEMS_SQL + 'AND key = ?'
        row = self.conn.execute(sql, (key,)).fetchone()
        if not row:
            return None

        e = Entry(**row)
        self._populate_entry(e)

        return e

    def modified_since(self, dt):
        """Iterate Entries modified since datetime."""
        sql = ITEMS_SQL + 'AND modified > ?'
        for row in self.conn.execute(sql, (dt2sqlite(dt),)):
            e = Entry(**row)
            self._populate_entry(e)
            yield e

    def all_entries(self):
        """Return all database entries."""
        for row in self.conn.execute(ITEMS_SQL):
            e = Entry(**row)
            self._populate_entry(e)
            yield e

    def _populate_entry(self, e):
        """Populate Entry's attributes from other tables."""
        # --------------------------------------------------
        # Defaults & empty attributes
        for k in ('collections', 'creators', 'attachments',
                  'notes', 'tags'):
            e[k] = []
        # Metadata
        e.title = u''
        e.date = None
        e.year = 0
        e.zdata = {}

        # Parseable attributes
        e.modified = sqlite2dt(e.modified)

        # --------------------------------------------------
        # Creators
        for row in self.conn.execute(CREATORS_SQL, (e.id,)):
            e.creators.append(Creator(**row))

        # --------------------------------------------------
        # Tags
        for row in self.conn.execute(TAGS_SQL, (e.id,)):
            e.tags.append(row['name'])

        # --------------------------------------------------
        # Collections
        for row in self.conn.execute(COLLECTIONS_SQL, (e.id,)):
            e.collections.append(Collection(**row))

        # --------------------------------------------------
        # Attachments
        for row in self.conn.execute(ATTACHMENTS_SQL, (e.id,)):
            key, path, title, url = (row['key'], row['path'],
                                     row['title'], row['url'])

            # Attachment may be in Zotero's storage somewhere, so
            # fix path to point to the right place.
            if path and not os.path.exists(path):
                for prefix in ('attachment:', 'storage:'):
                    if path.startswith(prefix):
                        path = path[len(prefix):]
                        # x = os.path.splitext(path)[1]
                        # if x not in ATTACHMENT_EXTS:
                        #     continue

                        path = os.path.join(self.storage_dir, key, path)

            e.attachments.append(Attachment(key=key, name=title, path=path,
                                            url=url))

        # --------------------------------------------------
        # Notes
        for row in self.conn.execute(NOTES_SQL, (e.id,)):
            html = row['note']
            e.notes.append(HTMLText.strip(html))

        # --------------------------------------------------
        # Other data
        for row in self.conn.execute(METADATA_SQL, (e.id,)):
            k, v = row['name'], row['value']

            if k == 'title':
                e.title = v

            elif k == 'date':
                # e.zdata['date'] = v
                # e.zdata['date_words'] = v.split()[-1]
                e.date = parse_date(v)
                e.year = int(v[:4])

            # everything goes in the `zdata` dict
            e.zdata[k] = v

        # Extract and set CSL data
        e.csl = csl.entry_data(e)

        return e

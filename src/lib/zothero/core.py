# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Main ZotHero API."""

from __future__ import print_function, absolute_import

import logging
import os

from .util import copyifnewer, unicodify, shortpath

# Default location of Zotero's data in version 5
DEFAULT_ZOTERO_DIR = u'~/Zotero'

log = logging.getLogger(__name__)


class ZotHero(object):
    """Main application object.

    This class is a thin wrapper around the worker classes

      - `zotero.Zotero`
      - `index.Index`
      - `styles.Styles`

    and provides a convenient, utility interface to them.

    Attributes:
        cachedir (str): Directory all cached data are stored in.

    """

    def __init__(self, cachedir, zot_data_dir=None, zot_attachments_dir=None):
        """Create new `ZotHero` using ``cachedir``.

        Args:
            cachedir (str): Directory to store cached data in.
            zot_data_dir (str, optional): Directory Zotero data are stored
                in. Defaults to the standard Zotero directory ``~/Zotero``.
            zot_attachments_dir (str, optional): Directory Zotero
                attachments are stored in. This should be set to the
                same as the "Linked Attachment Base Directory" set
                in Zotero's preferences (if one is set).

        """
        self.cachedir = cachedir

        # Copy of Zotero database. Zotero locks the original, so
        # it's necessary to make a copy.
        self._copy_path = os.path.join(cachedir, 'zotero.sqlite')

        # Attributes to back lazy-loading properties
        self._zotero_dir = zot_data_dir  # Zotero's data directory
        self._attachments_dir = zot_attachments_dir  # Zotero's attachment base
        self._zot = None  # Zotero object
        # self._cache = None  # Cache object
        self._index = None  # Index object
        self._styles = None  # Styles object

        log.debug('[core] cachedir=%r', shortpath(cachedir))
        log.debug('[core] zotero_dir=%r', shortpath(self.zotero_dir))
        log.debug('[core] attachments_dir=%r', shortpath(self.attachments_dir))

    @property
    def zotero_dir(self):
        """Path to Zotero's data folder.

        This is the folder where ``zotero.sqlite``, ``storage`` and
        ``styles`` are located.

        Set to the value of ``zot_data_directory`` passed to `__init__.py`
        or ``~/Zotero`` if no value for ``zot_data_directory`` was given.

        """
        if not self._zotero_dir:
            path = os.path.expanduser(DEFAULT_ZOTERO_DIR)
            if not os.path.exists(path):
                raise ValueError('Zotero directory does not exist: %r' % path)

            self._zotero_dir = path

        return self._zotero_dir

    @property
    def attachments_dir(self):
        """Path to Zotero's optional attachments base directory."""
        if self._attachments_dir:
            path = os.path.expanduser(self._attachments_dir)
            if not os.path.exists(path):
                raise ValueError('Attachments directory does not exist: %r' %
                                 path)

            return unicodify(path)

        return None

    @property
    def zotero(self):
        """Zotero instance.

        Initialses and returns a `.zotero.Zotero` instance
        based on :attr:`zotero_path`.

        Returns:
            .zotero.Zotero: Initialised `Zotero` object.

        """
        from .zotero import Zotero

        if not self._zot:
            original = os.path.join(self.zotero_dir, 'zotero.sqlite')
            if not os.path.exists(original):
                raise ValueError('Zotero database not found: %r' % original)

            # Ensure cached copy of database is up to date
            dbpath = copyifnewer(original, self._copy_path)

            self._zot = Zotero(self.zotero_dir, dbpath, self.attachments_dir)

            # Validate paths by calling storage & styles properties
            log.debug('[core] storage=%r', shortpath(self._zot.storage_dir))
            log.debug('[core] styles=%r', shortpath(self._zot.styles_dir))

        return self._zot

    @property
    def index(self):
        """Search index.

        Creates and returns an `Index` object. The index is initialised,
        but may be empty.

        Returns:
            .index.Index: Initialised search index.

        """
        if not self._index:
            from .index import Index
            self._index = Index(os.path.join(self.cachedir, 'search.sqlite'))
            # self._index.update(self.zotero)

        return self._index

    @property
    def stale(self):
        """Return ``True`` if search index isn't up to date."""
        if self.index.empty:
            return True

        return self.zotero.last_updated > self.index.last_updated

    def update_index(self, force=False):
        """Update the search index."""
        self.index.update(self.zotero, force)

    # @property
    # def cache(self):
    #     """Top-level cache."""
    #     if not self._cache:
    #         from .cache import Cache
    #         self._cache = Cache(os.path.join(self.cachedir, 'cache.sqlite'))

    #     return self._cache

    @property
    def styles(self):
        """CSL Styles loader.

        Returns:
            .styles.Styles: `Styles` object pointing to the styles directory
            of :attr:`zotero`.

        """
        if not self._styles:
            from .styles import Styles
            self._styles = Styles(self.zotero.styles_dir, self.cachedir)

        return self._styles

    def entry(self, entry_id):
        """Retrieve `Entry` for ``key``.

        Args:
            key (str): Zotero database key

        Returns:
            zothero.zotero.Entry: `Entry` for `key` or `None` if not found.

        """
        return self.index.entry(entry_id)

    def search(self, query):
        """Search the Zotero database."""
        log.info(u'[core] searching for "%s" ...', query)
        return self.index.search(query)

    def style(self, key):
        """Return CSL style for key."""
        return self.styles.get(key)

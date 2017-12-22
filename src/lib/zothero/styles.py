# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-18
#

"""CSL style handling.

The main class `Styles` fetches, loads and applies CSL styles.
"""

from __future__ import print_function, absolute_import

import logging
import json
import os

# RTF codec that registers itself
import rtfunicode

from .cache import Cache
from .models import CSLStyle
from .util import safename, shortpath, unicodify

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# CSL stylesheet namespace
NS = 'http://purl.org/net/xbiblio/csl'


# class RTFFormatter(object):
#     """citeproc formatter for RTF.

#     citeproc's Formatter API is insufficient for generating valid RTF,
#     so you must call `RTFFormatter.wrap()` on the result.
#     """

#     @staticmethod
#     def wrap(rtf):
#         """Wrap RTF snippet in document header & footer.

#         citeproc's handling is a bit shit, and it doesn't call `preformat`
#         on everthing, nor allow global "before" and "after" handlers.

#         As a result, it's necessary to RTF-encode the data here and
#         then put backslashes and newlines back into the text.

#         Finally, wrap the text in an RTF header and footer.

#         Args:
#             rtf (str): RTF snippet.

#         Returns:
#             str: RTF document.
#         """
#         rtf = rtf.encode('rtfunicode')
#         # Put backslashes and newlines back in
#         rtf = rtf.replace('\\u92?', '\\').replace('\\u10?', '\n')
#         # Wrap in RTF header and footer
#         return r'{\rtf1\ansi\deff0' + '\n' + rtf + '\n}'

#     def preformat(self, text):
#         return text

#     def Italic(self, text):
#         return '\\i ' + text + '\n\\i0 '

#     def Oblique(self, text):
#         return self.Italic(text)

#     def Light(self, text):
#         return text

#     def Underline(self, text):
#         return '\\ul ' + text + '\n\\ul0 '

#     def Superscript(self, text):
#         return '\\super ' + text + '\n\\super0 '

#     def Subscript(self, text):
#         return '\\sub ' + text + '\n\\sub0 '

#     def SmallCaps(self, text):
#         return '\\scaps ' + text + '\n\\scaps0 '


class Styles(object):
    """CSL style loader and manager.

    Reads (and caches) .csl files from disk and fetches them from URLs.

    Styles are loaded and the cache updated on instantiation.

    Attributes:
        cachedir (unicode): Directory to store metadata database in.
        dirpath (unicode): Directory to load .csl style definitions from.
        dldir (unicode): Directory CSL external stylesheets are downloaded to.
        store (cache.Store): `CSLStyle` cache.
    """

    def __init__(self, stylesdir, cachedir):
        """New Styles containing styles from ``stylesdir``.

        Args:
            stylesdir (unicode): Directory to load styles from.
            cachedir (unicode): Top-level cache directory.

        Raises:
            ValueError: Raised if ``stylesdir`` doesn't exist.

        """
        if not os.path.exists(stylesdir):
            raise ValueError('stylesdir does not exist: %r' % stylesdir)

        dldir = os.path.join(cachedir, 'styles')

        if not os.path.exists(dldir):
            os.makedirs(dldir)

        self.dirpath = stylesdir
        self.cachedir = cachedir
        self.dldir = dldir
        # Parent cache object
        self._cache = Cache(os.path.join(self.cachedir, 'styles.sqlite'))
        # Store for CSLStyle objects, keyed by URL
        self.store = self._cache.open('styles', json.dumps, CSLStyle.from_json)
        # Store for modtimes of the files the styles are loaded from,
        # keyed by filepath
        self._mtimes = self._cache.open('modtimes', json.dumps, json.loads)
        self.update()

    def get(self, key):
        """Return `CSLStyle` for key.

        Args:
            key (unicode): Unique key for style.

        Returns:
            models.CSLStyle: Style object for key, or ``None`` if not
                found.
        """
        return self.store.get(key)

    def canonical(self, key):
        """Resolve dependent styles and return the root style."""
        k = key  # preserve key for log message
        while True:
            s = self.get(k)
            if not s:
                break
            if not s.parent_url:
                break

            k = s.parent_url

        if k != key:
            log.debug('[styles] canonical style for "%s": %s', key, s)

        return s

    def all(self, hidden=False):
        """Iterate over all styles.

        Yields:
            models.CSLStyle: CSL style installed in Zotero.

        Args:
            hidden (bool, optional): Also return hidden styles.
        """
        for k in self.store.keys():
            style = self.store.get(k)
            if style.hidden and not hidden:
                continue

            yield style

    def cite(self, entry, style, bibliography=False, locale=None):
        """Formatted citation for an Entry.

        Generate and return HTML and RTF citations. The "text" format
        returned is also HTML (intended for use in Markdown documents).

        Args:
            entry (models.Entry): The Entry to create a citation for.
            style (models.CSLStyle): Style to apply to citation.
            bibliography (bool, optional): Generate bibliography-style
                citation, not citation-/note-style.
            locale (str, optional): Locale understood by citeproc.

        Returns:
            dict: Format -> citation mapping. Keys are ``html``, ``rtf``
                and ``text``.

        Raises:
            ValueError: Raised if style can't be found.
        """
        import cite
        from cite import locales

        key = style.key
        style = self.canonical(key)
        if not style:
            raise ValueError(u'could not resolve style ' + key)

        if locale:
            loc = locales.lookup(locale)
            if loc:
                locale = loc.code
            else:
                raise ValueError(u'unsupported locale: ' + locale)
                # log.error('[styles] unsupported locale: %s', locale)

        log.debug('[styles] locale=%r', locale)
        log.debug('[styles] style=%r', style)
        log.debug('[styles] csl=%r', [entry.csl])

        return cite.generate([entry.csl], style.path, bibliography, locale)

    def update(self):
        """Load CSL style definitions.

        Reads styles from :attr:`dirpath` and its ``hidden`` subdirectory,
        if it exists.

        Any files that haven't been changed since they were last read
        are ignored.

        After all styles have been read from disk, download any missing
        "parent" styles of dependent styles, and load those, too.

        Finally, remove any cached styles that have disappeared from
        disk.
        """
        # Parent URLs of dependent styles. After all styles are loaded,
        # any unresolved URLs are retrieved and loaded.
        parent_urls = []

        # Zotero stores parent stylesheets in a "hidden" directory.
        hidden = os.path.join(self.dirpath, 'hidden')
        if os.path.exists(hidden):
            parent_urls.extend(self._readdir(hidden, True))

        # Load user styles
        parent_urls.extend(self._readdir(self.dirpath))

        # --------------------------------------------------------------
        # Find unresolved URLs and retrieve them
        parent_urls = [u for u in parent_urls if not self.get(u)]
        for url in parent_urls:
            style = self._fetch_style(url)
            if style:
                style.hidden = True
                self._mtimes.set(style.path, os.path.getmtime(style.path))
                self.store.set(style.key, style)
                log.info(u'[styles] loaded "%s"', style.name)

        # --------------------------------------------------------------
        # Purge deleted styles from cache
        for style in self.all(True):
            if not os.path.exists(style.path):
                self._mtimes.delete(style.path)
                if self.store.delete(style.key):
                    log.debug(u'[styles] removed %s', style)

    def _readdir(self, dirpath, hidden=False):
        """Load CSL styles from ``dirpath``.

        Read any .csl files in ``dirpath``, ignoring those that haven't
        been modified since they were last loaded.

        Parse the files to extract title, URL and the URL of any parent
        style (for dependent stylesheets).

        Return a list of any parent URLs.

        Args:
            dirpath (unicode): Directory to read .csl files from.
            hidden (bool, optional): Mark loaded `CSLStyle` objects as
                hidden.

        Returns:
            list: URLs to parents of any dependent styles loaded.
        """
        parent_urls = []
        # Read styles in the styles directory and add them to or update
        # them in the cache
        for fn in os.listdir(dirpath):
            if not fn.lower().endswith('.csl'):
                continue

            path = os.path.join(dirpath, fn)

            # Ignore unchanged files
            mtime = os.path.getmtime(path)
            if mtime <= (self._mtimes.get(path) or 0):
                continue

            self._mtimes.set(path, mtime)

            # ----------------------------------------------------------
            # Parse style definition
            log.debug(u'[styles] reading "%s" ...', shortpath(path))

            style = self._load_style(path)
            if not style:
                log.warning(u'[styles] could not read style: %s',
                            shortpath(path))
                continue

            if style.parent_url:
                parent_urls.append(style.parent_url)

            style.hidden = hidden
            self.store.set(style.key, style)
            log.info(u'[styles] loaded %s', style)

        return parent_urls

    def _load_style(self, path):
        """Extract style info from a .csl file.

        Args:
            path (unicode): Path to a .csl file.

        Returns:
            models.CSLStyle: Style parsed from .csl file or ``None`` if
                the file couldn't be parsed.
        """
        try:
            import xml.etree.cElementTree as ET
        except ImportError:  # pragma: no cover
            import xml.etree.ElementTree as ET

        name = parent_url = url = None

        root = ET.parse(path)
        elem = root.find('.//{%s}title' % NS)

        if elem is None:  # invalid style
            log.error(u'[styles] no title found: %s', shortpath(path))
            return None

        name = unicodify(elem.text)

        # Find own URL and possible URL of parent style
        for elem in root.findall('.//{%s}link' % NS):

            rel = elem.attrib.get('rel')
            if rel == 'self':  # style's own URL
                url = elem.attrib.get('href')

            elif rel == 'independent-parent':  # URL of canonical definition
                parent_url = elem.attrib.get('href')

        return CSLStyle(name=name, url=url, path=path, parent_url=parent_url)

    def _fetch_style(self, url):
        """Generate `CSLStyle` from a remote .csl file.

        Args:
            url (unicode): URL to retrieve .csl stylesheet from.

        Returns:
            models.CSLStyle: Style parsed from .csl file or ``None``
                if the URL couldn't be retrieved or the file parsed.
        """
        path = os.path.join(self.dldir, safename(url) + '.csl')

        if not os.path.exists(path):
            from urllib import urlretrieve
            log.debug('[styles] downloading "%s" to "%s" ...', url,
                      shortpath(path))

            try:

                path, h = urlretrieve(url, path)
                log.debug('[styles] headers=%r', h)

            except Exception as err:
                log.error('[styles] error retrieving "%s": %s', url, err)
                return None

        return self._load_style(path)

#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-18
#

"""CSL styles and handlers."""

from __future__ import print_function, absolute_import

import logging
import json
import os

import rtfunicode

from .models import CSLStyle
from .util import unicodify

log = logging.getLogger(__name__)


class RTFFormatter(object):
    """citeproc formatter for RTF."""

    @staticmethod
    def wrap(rtf):
        """Wrap RTF snippet in document header & footer.

        citeproc's handling is a bit shit, and it doesn't call `preformat`
        on everthing, nor allow global "before" and "after" handlers.

        As a result, it's necessary to RTF-encode the data here and
        then put backslashes and newlines back into the text.

        Finally, wrap the text in an RTF header and footer.

        Args:
            rtf (str): RTF snippet.

        Returns:
            str: RTF document.
        """
        rtf = rtf.encode('rtfunicode')
        # Put backslashes and newlines back in
        rtf = rtf.replace('\\u92?', '\\').replace('\\u10?', '\n')
        return r'{\rtf1\ansi\deff0' + '\n' + rtf + '\n}'

    def preformat(self, text):
        return text

    def Italic(self, text):
        return '\\i ' + text + '\n\\i0 '

    def Oblique(self, text):
        return self.Italic(text)

    def Light(self, text):
        return text

    def Underline(self, text):
        return '\\ul ' + text + '\n\\ul0 '

    def Superscript(self, text):
        return '\\super ' + text + '\n\\super0 '

    def Subscript(self, text):
        return '\\sub ' + text + '\n\\sub0 '

    def SmallCaps(self, text):
        return '\\scaps ' + text + '\n\\scaps0 '


class Styles(object):
    """CSL style manager and loader.

    Attributes:
        dirpath (unicode): Directory to load .csl style definitions from.
        store (zothero.cache.store): `CSLStyle` cache.
    """

    def __init__(self, stylesdir, cache):
        """New Styles containing styles from ``stylesdir``.

        Args:
            stylesdir (unicode): Directory to load styles from.
            cache (zothero.cache.cache): Cache object in which to create
                styles Store.

        Raises:
            ValueError: Raised if ``stylesdir`` doesn't exist.
        """
        if not os.path.exists(stylesdir):
            raise ValueError('stylesdir does not exist: %r' % stylesdir)

        self.dirpath = stylesdir
        self.store = cache.open('styles', json.dumps, CSLStyle.from_json)
        self.update()

    def get(self, key):
        """Return `CSLStyle` for key."""
        return self.store.get(key)

    def all(self):
        """Iterate over all styles.

        Yields:
            models.CSLStyle: CSL style installed in Zotero.
        """
        for k in self.store.keys():
            yield self.store.get(k)

    def cite(self, entry, style):
        """Formatted citation for an Entry.

        Generate and return HTML and RTF citations. The "text" format
        returned is also HTML (intended for use in Markdown documents).

        Args:
            entry (models.Entry): The Entry to create a citation for.
            style (models.CSLStyle): Style to apply to citation.

        Returns:
            dict: Format -> citation mapping. Keys are ``html``, ``rtf``
                and ``text``.
        """
        from citeproc import (
            Citation,
            CitationItem,
            CitationStylesBibliography,
            CitationStylesStyle,
        )
        from citeproc import formatter
        from citeproc.source.json import CiteProcJSON

        log.debug('[styles] style=%r', style)
        log.debug('[styles] csl=%r', [entry.csl])

        def warn(item):
            log.error('[styles] Reference with key "%s" not in bibliography',
                      item.key)

        # Citation data and style
        bib_data = CiteProcJSON([entry.csl])
        bib_style = CitationStylesStyle(style.path, validate=False)

        # HTML generator
        bib_html = CitationStylesBibliography(bib_style, bib_data,
                                              formatter.html)
        cite = Citation([CitationItem(entry.key)])
        bib_html.register(cite)

        html = u''.join(bib_html.cite(cite, warn))
        log.debug(u'[styles] html=%s', html)

        # RTF generator
        bib_rtf = CitationStylesBibliography(bib_style, bib_data,
                                             RTFFormatter())
        bib_rtf.register(cite)

        rtf = u''.join(bib_rtf.cite(cite, warn))
        # Turn RTF snippet into a valid document, so pasting works
        rtf = RTFFormatter.wrap(rtf)
        log.debug(u'[styles] rtf=%s', rtf)

        return dict(html=html, text=html, rtf=rtf)

    def update(self):
        """Load styles."""
        keys = set()  # all available styles

        # Read styles in the styles directory and add them to or update
        # them in the cache
        for fn in os.listdir(self.dirpath):
            if not fn.lower().endswith('.csl'):
                continue

            path = os.path.join(self.dirpath, fn)
            key = os.path.splitext(fn)[0].lower()
            keys.add(key)

            mtime = os.path.getmtime(path)
            cached = self.store.updated(key)
            if mtime <= cached:
                continue

            log.debug(u'[styles] reading "%s" ...', path)

            style = self._load_style(path)
            if not style:
                log.warning(u'[styles] could not read style: %s', key)
                continue

            self.store.set(style.key, style)
            log.info(u'[styles] loaded %s', style)

        # Purge deleted styles from cache
        for key in self.store.keys():
            if key not in keys:
                style = self.store.get(key)
                if self.store.delete(key):
                    log.debug(u'[styles] removed %s', style)

    def _load_style(self, path):
        """Extract style info from a .csl file."""
        from lxml import etree
        ns = {'csl': 'http://purl.org/net/xbiblio/csl'}
        root = etree.parse(path)
        elem = root.find('.//csl:title', namespaces=ns)
        if elem is not None:
            return CSLStyle(name=unicodify(elem.text), path=path)

        return None

# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-22
#

"""Convert HTML to RTF."""

from __future__ import print_function, absolute_import

from HTMLParser import HTMLParser
import logging

# RTF codec that registers itself
import rtfunicode


log = logging.getLogger(__name__)


class Converter(HTMLParser):
    """Convert HTML to RTF."""

    @classmethod
    def convert(cls, html):
        p = cls()
        p.feed(html)
        return str(p)

    def __init__(self):
        self.reset()
        self.data = []

    def handle_starttag(self, tag, attr):
        if tag == 'i':
            self.data.append('\\i ')

        elif tag == 'b':
            self.data.append('\\b ')

        elif tag in ('sup', 'super'):
            self.data.append('\\super ')

        else:
            log.warning('[html2rtf] unknown tag: %s', tag)

    def handle_endtag(self, tag):
        if tag == 'i':
            self.data.append('\n\\i0 ')

        elif tag == 'b':
            self.data.append('\n\\b0 ')

        elif tag in ('sup', 'super'):
            self.data.append('\n\\super0 ')

        else:
            log.warning('[html2rtf] unknown tag: %s', tag)

    def handle_data(self, s):
        self.data.append(s.encode('rtfunicode'))

    def __str__(self):
        """Return RTF."""
        data = ['{\\rtf1\\ansi\\deff0\n']  # RTF header
        data.extend(self.data)
        data += ['\n}']  # RTF footer
        return ''.join(data)


def html2rtf(html):
    """Convert HTML to RTF."""
    return Converter.convert(html)

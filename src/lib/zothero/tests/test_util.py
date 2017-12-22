# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Unit tests for util.py"""

from __future__ import print_function, absolute_import

import pytest

from zothero.util import asciify, HTMLText, safename


def test_strip_tags():
    """Strip HTML tags."""
    data = [
        ('<p>Test</p>', u'Test'),
        ('The <em>best</em> ever', u'The best ever'),
        ('<h1>Fööbär</h1>', u'Fööbär'),
    ]

    for html, text in data:
        res = HTMLText.strip(html)
        assert res == text


def test_asciify():
    """ASCII-fy strings."""
    data = [
        (u'Ärger', u'Arger'),
        ('Ärger', u'Arger'),
    ]

    for s, x in data:
        r = asciify(s)
        assert r == x
        assert isinstance(r, unicode)


def test_safename():
    """Filesystem-safe names."""
    data = [
        (u'Ärger', u'arger'),
        ('https://www.google.com', u'https-www.google.com'),
        (u'12345', u'12345'),
    ]
    for s, x in data:
        r = safename(s)
        assert r == x
        assert isinstance(r, unicode)


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])

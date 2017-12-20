#!/usr/bin/env python
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

import os
import sys

import pytest

from zothero.util import HTMLText


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


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])

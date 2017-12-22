# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Icons for Zotero entries."""

from __future__ import print_function, absolute_import

import os

# Where the icons are stored
ICONDIR = os.path.abspath(os.path.dirname(__file__))

# Mapping of Zotero item types to icon basenames.
TYPE2ICON = {
    'journalArticle': 'article',
    'book': 'book',
    'bookSection': 'chapter',
    'conferencePaper': 'conference',
    'webpage': 'webpage',
}


def entry_icon(e):
    """Return the appropriate icon for an `Entry`."""
    basename = TYPE2ICON.get(e.type, 'written')

    if e.attachments:
        basename += '-with-attachment'

    return os.path.join(ICONDIR, 'icons', basename + '.png')

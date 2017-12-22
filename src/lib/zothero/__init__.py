# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-15
#

"""Zotero workflow for Alfred."""

from __future__ import print_function, absolute_import
from .core import ZotHero

# Populated by `zh` when it runs. Not a best practice, but it saves
# having to pass a Context around everywhere.
app = None

# encoding: utf-8
#
# Copyright (c) 2019 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2019-01-06
#

"""Read Zotero configuration files."""

from ConfigParser import SafeConfigParser
import logging
import os
import re

from .util import unicodify

CONFDIR = os.path.expanduser(u'~/Library/Application Support/Zotero')
PROFILES = os.path.join(CONFDIR, u'profiles.ini')
DATADIR_KEY = 'extensions.zotero.dataDir'
ATTACH_KEY = 'extensions.zotero.baseAttachmentPath'
# Start of preference lines
PREFIX = 'user_pref("'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def read():
    """Load data and attachments directories from Zotero prefs."""
    p = find_prefs()
    if p:
        return parse_prefs(p)

    return None, None


def find_prefs():
    """Find prefs.js by parsing profiles.ini."""
    conf = SafeConfigParser()
    try:
        conf.read(PROFILES)
    except Exception as err:
        log.error('reading profiles.ini: %s', err)
        return None

    for section in conf.sections():
        if conf.has_option(section, 'Name') and \
                conf.get(section, 'Name') == 'default':
            path = conf.get(section, 'Path')
            if conf.getboolean(section, 'IsRelative'):
                path = os.path.join(CONFDIR, path)

            return unicodify(os.path.join(path, 'prefs.js'))

    return None


def parse_prefs(path):
    """Extract relevant preferences from prefs.js."""
    datadir = attachdir = None

    def extract_value(s):
        m = re.search(r'"(.+)"', s)
        if not m:
            return None

        return unicodify(m.group(1))

    with open(path) as fp:
        for line in fp:
            line = line.strip()
            if not line.startswith(PREFIX):
                continue

            line = line[len(PREFIX):]
            i = line.find('",')
            if i < 0:
                continue

            key = line[:i]
            if key == DATADIR_KEY:
                datadir = extract_value(line[i + 2:])
                log.debug('[config] datadir=%r', datadir)
            elif key == ATTACH_KEY:
                attachdir = extract_value(line[i + 2:])
                log.debug('[config] attachdir=%r', attachdir)

    return datadir, attachdir

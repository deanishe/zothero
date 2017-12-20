#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-18
#

"""Zotero to CSL mappings."""

from __future__ import print_function, absolute_import

from collections import defaultdict
import logging

from . import util


log = logging.getLogger(__name__)


# CSL fields that should be formatted as dates
CSL_DATE_KEYS = (u'issued', u'accessed', u'event-date',
                 u'original-date', u'submitted')


def get_field(zfield, ztype):
    """Convert Zotero field name to CSL field name.

    CSL field name corresponding to a Zotero field. Returns ``None``
    if there is no corresponding CSL field.

    Args:
        zfield (unicode): Zotero field name.
        ztype (unicode): Zotero entry type, e.g. "book".

    Returns:
        unicode: CSL field name or ``None``.
    """
    # Get "canonical" Zotero field name
    zfield = REMAP.get(zfield, zfield)
    # Try type-specific field first
    return FIELD_MAP.get(ztype + u'::' + zfield, FIELD_MAP.get(zfield))


def get_creator(ztype):
    """Convert Zotero creator type to CSL creator type.

    CSL creator type corresponding to a Zotero type. Returns ``None``
    if there is no corresponding CSL type.

    Args:
        ztype (unicode): Zotero creator type.

    Returns:
        unicode: CSL creator type or ``None``.
    """
    # Get "canonical" Zotero type
    ztype = REMAP.get(ztype, ztype)
    return CREATOR_MAP.get(ztype)


def get_type(ztype):
    """Convert Zotero publication type to CSL publication type.

    CLS publication type corresponding to the Zotero one. Return ``None``
    if there is no corresponding CSL type.

    Args:
        ztype (unicode): Zotero publication type.

    Returns:
        unicode: CSL type  or ``None``.
    """
    # Get "canonical" Zotero type
    ztype = REMAP.get(ztype, ztype)
    return TYPE_MAP.get(ztype)


def convert_creator(zc):
    """Convert Zotero Creator into CSL creator."""
    if zc.family is None:  # nameless
        return None, None

    d = {'family': zc.family}

    ctype = get_creator(zc.type)
    if not ctype:  # unknown type
        return None, None

    if zc.given:
        d['given'] = zc.given

    return d, ctype


def entry_data(e):
    """Get CSL(JSON) data for an Entry.

    The data are compatible with CSL-JSON.

    Args:
        e (models.Entry): Entry to generate data for.

    Returns:
        dict: CSL data.
    """
    data = {'id': e.key}
    ctype = get_type(e.type)
    if not ctype:
        log.warning('[csl] unknown type: %r', e)
        return {}

    data['type'] = ctype

    creators = defaultdict(list)

    for zc in e.creators:
        d, ctype = convert_creator(zc)
        if not d:
            log.warning('[csl] invalid creator %r for %r', zc, e)
        else:
            creators[ctype].append(d)

    data.update(creators)

    for zk, v in e.zdata.items():
        ck = get_field(zk, e.type)
        if ck:
            if ck in CSL_DATE_KEYS:
                v = parse_date(v)
            data[ck] = v

    return data


def parse_date(datestr):
    """Parse a Zotero date string into CSL(JSON) ``date-parts``.

    Args:
        datestr (unicode): Zotero date string.

    Returns:
        dict: ``date-parts`` dict for CSL JSON.
    """
    parsed = util.parse_date(datestr)
    if parsed:
        parts = [int(s) for s in parsed.split('-')]
    else:
        parts = [int(datestr[:4])]

    return {'date-parts': [parts]}


# Zotero field to other Zotero field
REMAP = {
    u'artist': u'author',
    u'artworkMedium': u'medium',
    u'audioFileType': u'medium',
    u'audioRecordingFormat': u'medium',
    u'billNumber': u'number',
    u'blogTitle': u'publicationTitle',
    u'bookTitle': u'publicationTitle',
    u'cartographer': u'author',
    u'caseName': u'title',
    u'codePages': u'pages',
    u'codeVolume': u'volume',
    u'company': u'publisher',
    u'contributor': u'author',
    u'dateDecided': u'date',
    u'dateEnacted': u'date',
    u'dictionaryTitle': u'publicationTitle',
    u'director': u'author',
    u'distributor': u'publisher',
    u'docketNumber': u'number',
    u'documentNumber': u'number',
    u'encyclopediaTitle': u'publicationTitle',
    u'episodeNumber': u'number',
    u'firstPage': u'pages',
    u'forumTitle': u'publicationTitle',
    u'genre': u'type',
    u'institution': u'publisher',
    u'interviewMedium': u'medium',
    u'interviewee': u'author',
    u'inventor': u'author',
    u'issueDate': u'date',
    u'label': u'publisher',
    u'letterType': u'type',
    u'manuscriptType': u'type',
    u'mapType': u'type',
    u'nameOfAct': u'title',
    u'network': u'publisher',
    u'patentNumber': u'number',
    u'performer': u'author',
    u'podcaster': u'author',
    u'postType': u'type',
    u'presentationType': u'type',
    u'presenter': u'author',
    u'proceedingsTitle': u'publicationTitle',
    u'programTitle': u'publicationTitle',
    u'programmer': u'author',
    u'publicLawNumber': u'number',
    u'reportNumber': u'number',
    u'reportType': u'type',
    u'reporterVolume': u'volume',
    u'sponsor': u'author',
    u'studio': u'publisher',
    u'subject': u'title',
    u'thesisType': u'type',
    u'university': u'publisher',
    u'videoRecordingFormat': u'medium',
    u'websiteTitle': u'publicationTitle',
    u'websiteType': u'type',
    u'websiteType': u'type',
}

# Zotero data field types to CSL field types
FIELD_MAP = {
    u'DOI': u'DOI',
    u'ISBN': u'ISBN',
    u'ISSN': u'ISSN',
    u'abstractNote': u'abstract',
    u'accessDate': u'accessed',
    u'applicationNumber': u'call-number',
    u'archive': u'archive',
    u'archiveLocation': u'archive_location',
    u'artworkSize': u'dimensions',
    u'callNumber': u'call-number',
    u'code': u'container-title',
    u'codeNumber': u'volume',
    u'committee': u'section',
    u'conferenceName': u'event',
    u'court': u'authority',
    u'date': u'issued',
    u'distributor': u'publisher',
    u'edition': u'edition',
    u'extra': u'note',
    u'filingDate': u'submitted',
    u'history': u'references',
    u'issue': u'issue',
    u'issuingAuthority': u'authority',
    u'journalAbbreviation': u'journalAbbreviation',
    u'language': u'language',
    u'legalStatus': u'status',
    u'legislativeBody': u'authority',
    u'libraryCatalog': u'source',
    u'medium': u'medium',
    u'meetingName': u'event',
    u'numPages': u'number-of-pages',
    u'number': u'number',
    u'numberOfVolumes': u'number-of-volumes',
    u'pages': u'page',
    u'conferencePaper::place': u'event-place',
    u'place': u'publisher-place',
    u'priorityNumbers': u'issue',
    u'programmingLanguage': u'genre',
    u'publicationTitle': u'container-title',
    u'publisher': u'publisher',
    u'references': u'references',
    u'reporter': u'container-title',
    u'runningTime': u'dimensions',
    u'scale': u'scale',
    u'section': u'section',
    u'series': u'collection-title',
    u'seriesNumber': u'collection-number',
    u'seriesTitle': u'collection-title',
    u'session': u'chapter-number',
    u'shortTitle': u'shortTitle',
    u'system': u'medium',
    u'title': u'title',
    u'type': u'genre',
    u'url': u'URL',
    u'version': u'version',
    u'volume': u'volume',
}

# Zotero creator types to CSL creator types
CREATOR_MAP = {
    u'author': u'author',
    u'bookAuthor': u'container-author',
    u'composer': u'composer',
    u'director': u'director',
    u'editor': u'editor',
    u'interviewer': u'interviewer',
    u'recipient': u'recipient',
    u'reviewedAuthor': u'reviewed-author',
    u'seriesEditor': u'collection-editor',
    u'translator': u'translator',
}

# Zotero entry types to CSL entry types
TYPE_MAP = {
    u'artwork': u'graphic',
    u'attachment': u'article',
    u'audioRecording': u'song',
    u'bill': u'bill',
    u'blogPost': u'post-weblog',
    u'book': u'book',
    u'bookSection': u'chapter',
    u'case': u'legal_case',
    u'computerProgram': u'book',
    u'conferencePaper': u'paper-conference',
    u'dictionaryEntry': u'entry-dictionary',
    u'document': u'article',
    u'email': u'personal_communication',
    u'encyclopediaArticle': u'entry-encyclopedia',
    u'film': u'motion_picture',
    u'forumPost': u'post',
    u'hearing': u'bill',
    u'instantMessage': u'personal_communication',
    u'interview': u'interview',
    u'journalArticle': u'article-journal',
    u'letter': u'personal_communication',
    u'magazineArticle': u'article-magazine',
    u'manuscript': u'manuscript',
    u'map': u'map',
    u'newspaperArticle': u'article-newspaper',
    u'note': u'article',
    u'patent': u'patent',
    u'podcast': u'song',
    u'presentation': u'speech',
    u'radioBroadcast': u'broadcast',
    u'report': u'report',
    u'statute': u'legislation',
    u'thesis': u'thesis',
    u'tvBroadcast': u'broadcast',
    u'videoRecording': u'motion_picture',
    u'webpage': u'webpage',
}

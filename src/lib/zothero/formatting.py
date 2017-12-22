# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-16
#

"""Format `models.Entry` for display."""

from __future__ import print_function, absolute_import

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EntryFormatter(object):
    """Formats an `Entry` for display."""

    def __init__(self, entry):
        """Create new `EntryFormatter` for `Entry`."""
        self.e = entry

    @property
    def title(self):
        """Properly formatted title.

        Returns 'xxx.' if title is empty, and appends a full stop
        if title does not already end with punctuation.

        Returns:
            unicode: Formatted title.
        """
        title = self.e.title

        if not title:
            return u'xxx.'

        if title[-1] not in '.?!':
            return title + '.'

        return title

    @property
    def creators(self):
        """Properly formatted authors.

        Returns 'xxx.' if there are no creators, otherwise joins
        them with commas & "and", and adds a full stop.

        Returns:
            unicode: Formatted list of creators.
        """
        n = len(self.e.creators)
        if n == 0:
            return u'xxx.'

        creators = []
        for c in self.e.creators:
            name = c.family
            i = c.index
            if c.type == 'editor':
                name += ' (ed.)'
            elif c.type == 'translator':
                name += ' (trans.)'

            creators.append((i, name))

        # Sort creators by index priority, then alphabetically
        creators.sort()
        names = [t[1] for t in creators]

        if n == 1:
            ref = names[0]

        elif n == 2:
            ref = ' and '.join(names)

        else:
            ref = ', '.join(names[:-1])
            ref = u'{}, and {}'.format(ref, names[-1])

        if ref and ref[-1] not in '.!?':
            ref += '.'

        return ref

    @property
    def year(self):
        """Formatted year.

        Returns "xxx." if year is unset, otherwise "YYYY."

        Returns:
            unicode: Formatted year.
        """
        if not self.e.year:
            return 'xxx.'

        return str(self.e.year) + '.'

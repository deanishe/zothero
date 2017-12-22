# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-22
#

"""Generate CSL citations."""

from __future__ import print_function, absolute_import

import json
import logging
import os
import subprocess

from .html2rtf import html2rtf

log = logging.getLogger(__name__)

# Ruby executable that generates the citation
PROG = os.path.join(os.path.dirname(__file__), 'cite')


class CitationError(Exception):
    """Raised if call to ``cite`` program fails."""


def generate(csldata, cslfile, bibliography=False, locale=None):
    """Generate an HTML & RTF citation for ``csldata`` using ``cslfile``."""
    js = json.dumps(csldata)

    cmd = [PROG, '--verbose']
    if bibliography:
        cmd.append('--bibliography')
    if locale:
        cmd += ['--locale', locale]

    cmd.append(cslfile)

    log.debug('[cite] cmd=%r', cmd)

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    stdout, stderr = p.communicate(js)
    if p.returncode:
        raise CitationError('cite exited with %d: %s', p.returncode, stderr)

    html = stdout.decode('utf-8')
    log.debug('[cite] html=%r', html)

    rtf = html2rtf(html)
    log.debug('[cite] rtf=%r', rtf)

    return dict(html=html, text=html, rtf=rtf)

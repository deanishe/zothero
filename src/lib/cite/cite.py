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
import subprocess  # nosec
from tempfile import NamedTemporaryFile

from .locales import LOCALE_DIR


log = logging.getLogger(__name__)

# Ruby executable that generates the citation
PROG = os.path.join(os.path.dirname(__file__), 'cite')


class CitationError(Exception):
    """Raised if call to ``cite`` program fails."""


def generate(csldata, cslfile, bibliography=False, locale=None):
    """Generate an HTML & RTF citation for ``csldata`` using ``cslfile``."""
    with NamedTemporaryFile(suffix='.json') as fp:
        json.dump(csldata, fp)
        fp.flush()

        cmd = [PROG, '--verbose', '--locale-dir', LOCALE_DIR]
        if bibliography:
            cmd.append('--bibliography')
        if locale:
            cmd += ['--locale', locale]

        cmd += [cslfile, fp.name]

        log.debug('[cite] cmd=%r', cmd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,  # nosec
                             stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        if p.returncode:
            raise CitationError('cite exited with %d: %s', p.returncode,
                                stderr)

    data = json.loads(stdout)
    html = data['html']

    log.debug('[cite] html=%r', html)

    rtf = '{\\rtf1\\ansi\\deff0 ' + data['rtf'] + '}'
    log.debug('[cite] rtf=%r', rtf)

    return dict(html=html, text=html, rtf=rtf)

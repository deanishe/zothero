import json
import logging
import os
import sys
import sqlite3

from .config import read as read_config

log = logging.getLogger(__name__)
datadir, _ = config = read_config()

SQL = "SELECT data FROM `better-bibtex` WHERE name = 'better-bibtex.citekey';"


class BetterBibTex:
    def __init__(self, zot_data_dir=None):
        dbpath = os.path.join(zot_data_dir or datadir, 'better-bibtex.sqlite')
        self.conn = None

        if os.path.exists(dbpath):
            try:
                self.conn = sqlite3.connect(dbpath)
            except Exception as e:
                log.warn('Open Better Bibtex database error: ' + str(e))
                return
        else:
            log.warn('Better Bibtex database not found')
            return

        try:
            row = self.conn.execute(SQL).fetchone()
            data = json.loads(row[0])['data']
            self.refkeys = {(str(ck['libraryID']), ck['itemKey']):
                            ck['citekey']
                            for ck in data}
        except Exception:
            log.warn('Better Bibtex database corrupted')

    def search(self, url):
        ''' given alfred item '''
        if self.conn is None or len(url) == 0:
            return []
        lib_id, key = url.split('/')[-1].split('_')
        return self.refkeys[(lib_id, key)]

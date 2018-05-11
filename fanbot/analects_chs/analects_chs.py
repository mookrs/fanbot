#!/usr/bin/env python3
from ..basebot import BaseBot, get_abs_path
from ..db import Database

DATABASE = get_abs_path(__file__, 'analects_chs.db')
db = Database(DATABASE)
STATUS_PREFIX = '【译文】'
MAX_ID = 241


class AnalectsChsBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(AnalectsChsBot, self).__init__(*args, **kwargs)

    def run(self):
        row_id = self._get_current_index()
        self._set_next_index(row_id, MAX_ID)

        row = db.query('SELECT * FROM analects WHERE rowid={};'.format(row_id), one=True)
        content, explanation = row['content'], row['explanation']

        status_content = content
        status_explanation = '{}{}'.format(STATUS_PREFIX, explanation)

        chunks_content = self.get_chunks(status_content)
        chunks_explanation = self.get_chunks(status_explanation)

        for chunk in chunks_explanation:
            self.update_status(chunk)
        for chunk in chunks_content:
            self.update_status(chunk)

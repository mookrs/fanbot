#!/usr/bin/env python3
from ..basebot import BaseBot, get_abs_path
from ..db import DBHelper

DATABASE = get_abs_path(__file__, 'taoteching.db')
db = DBHelper(DATABASE)
MAX_ID = 81


class TaoTeChingBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(TaoTeChingBot, self).__init__(*args, **kwargs)

    def run(self):
        row_id = self._get_current_index()
        self._increase_index(0 if row_id == MAX_ID else row_id)

        row = db.query('SELECT * FROM taoteching WHERE rowid={};'.format(row_id), one=True)
        content, explanation = row['content'], row['explanation']

        chunks_content = self.get_chunks(content)
        chunks_explanation = self.get_chunks(explanation)

        for chunk in chunks_explanation:
            self.update_status(chunk)
        for chunk in chunks_content:
            self.update_status(chunk)

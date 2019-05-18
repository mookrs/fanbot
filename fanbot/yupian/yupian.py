#!/usr/bin/env python3
from ..basebot import BaseBot, get_abs_path
from ..db import Database

DATABASE = get_abs_path(__file__, 'yupian.db')
db = Database(DATABASE)


class Bot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def run(self):
        row_id = self._get_current_index()
        self._set_next_index(row_id)

        row = db.query('SELECT * FROM yupian WHERE rowid={};'.format(row_id), one=True)
        radical, character, explaination = row['radical'], row['character'], row['explaination']

        status = '【{}部】【{}】{}'.format(radical, character, explaination)
        chunks = self.get_chunks(status)

        for chunk in chunks:
            self.update_status(chunk)

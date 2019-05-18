#!/usr/bin/env python3
from ..basebot import BaseBot, get_abs_path
from ..db import Database

DATABASE = get_abs_path(__file__, 'shuowen.db')
db = Database(DATABASE)


class Bot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def run(self):
        row_id = self._get_current_index()
        self._set_next_index(row_id)

        row = db.query('SELECT * FROM shuowen WHERE id="{}";'.format(row_id), one=True)
        radical, character, pinyin, explaination, fanqie = row['radical'], row['character'], row['pinyin'], row['explaination'], row['fanqie']

        # NOTE: 7 个字没有反切
        status = '【{}】【{}】【{}|{}】{}'.format(radical, character, pinyin, fanqie, explaination)
        chunks = self.get_chunks(status)

        for chunk in chunks:
            self.update_status(chunk)

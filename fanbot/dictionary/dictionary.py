#!/usr/bin/env python3
from ..basebot import BaseBot, get_abs_path
from ..db import DBHelper

DATABASE = get_abs_path(__file__, 'dictionary.db')
db = DBHelper(DATABASE)


class DictionaryBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(DictionaryBot, self).__init__(*args, **kwargs)

    def make_status(self):
        row_id = self._get_current_index()
        self._increase_index(row_id)

        code = 'CP000000000' + str(10000000 + row_id)
        row = db.query('SELECT * FROM xinhua WHERE code="{}";'.format(code), one=True)
        item, explanation, item_type = row['item'], row['explanation'], row['type']

        # NOTE:
        # 1 单字 2 词语
        # 3 Unicode扩展区或用繁体代替的字
        # 4 Unicode扩展区或用繁体代替的词语
        # 5 重复项 6 页面不存在
        status = '{} {}'.format(item, explanation) if item_type in (1, 4) else None
        return status

    def run(self):
        status = self.make_status()
        while status is None:
            status = self.make_status()

        chunks = self.get_chunks(status)
        for chunk in chunks:
            self.update_status(chunk)
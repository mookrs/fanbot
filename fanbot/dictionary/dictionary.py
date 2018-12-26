#!/usr/bin/env python3
from ..basebot import BaseBot, get_abs_path
from ..db import Database

DATABASE = get_abs_path(__file__, 'dictionary.db')
db = Database(DATABASE)


class DictionaryBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(DictionaryBot, self).__init__(*args, **kwargs)

    def make_status(self):
        row_id = self._get_current_index()
        self._set_next_index(row_id)

        code = 'CP000000000' + str(10000000 + row_id)
        row = db.query("SELECT * FROM xinhua WHERE code='{}';".format(code), one=True)
        item, explanation, item_type = row['item'], row['explanation'], row['type']

        # type 表示的含义:
        # 1 单字 2 词语
        # 3 Unicode 扩展区的字
        # 4 生造字或词语，未来可能出现在 Unicode 中
        # 5 重复项或页面不存在
        status = '{} {}'.format(item, explanation) if item_type in (1, 3) else None
        return status

    def run(self):
        status = self.make_status()
        while status is None:
            status = self.make_status()

        chunks = self.get_chunks(status)
        for chunk in chunks:
            self.update_status(chunk)

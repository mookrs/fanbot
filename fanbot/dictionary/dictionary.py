from ..basebot import BaseBot, get_abs_path
from ..db import Database

DATABASE = get_abs_path(__file__, 'dictionary.db')
db = Database(DATABASE)
MAX_ID = 12394


class Bot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def make_status(self):
        row_id = self._get_current_index()
        self._set_next_index(row_id, MAX_ID)

        code = 'CP000000000' + str(10000000 + row_id)
        row = db.query(f"SELECT * FROM xinhua WHERE code='{code}';", one=True)
        item, definition, item_type = row['item'], row['definition'], row['type']

        # type 表示的含义:
        # 1 单字
        # 2 词语
        # 3 Unicode 扩展区的单字
        # 4 使用 Ideographic Description Sequences (IDS) 描述的单字
        # 5 使用 Ideographic Description Sequences (IDS) 描述的词语
        # 6 重复项或页面不存在
        status = f'{item} {definition}' if item_type in (1, 3, 4) else None
        return status

    def run(self):
        status = self.make_status()
        while status is None:
            status = self.make_status()

        chunks = self.get_chunks(status)
        for chunk in chunks:
            self.update_status(chunk)

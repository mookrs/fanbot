#!/usr/bin/env python3
import feedparser

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import Database

DATABASE = get_abs_path(__file__, 'word_of_the_day.db')
db = Database(DATABASE)
FEED_URL = 'http://www.macmillandictionary.com/wotd/wotdrss.xml'


class Bot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS wotd (`id`, `title`, `summary`, `link`)')

        parsed_feed = feedparser.parse(FEED_URL)
        entry = parsed_feed.entries[-1]

        id = entry.id.split(',')[1]
        record = db.query('SELECT * FROM wotd WHERE id=?', (id,))
        if not record:
            title = entry.title
            summary = entry.summary
            link = entry.link

            data = (id, title, summary, entry.link)
            db.execute(
                'INSERT INTO wotd (`id`, `title`, `summary`, `link`) VALUES (?,?,?,?)', data)
            db.commit()

            status = '{}: {} {}'.format(title, summary, link)
            status_len = len('{}: {}'.format(title, summary)) + 21  # t.fanfou.com/********
            if status_len > 140:
                status = '{} {}: {}'.format(link, title, summary)

            self.update_status(status)

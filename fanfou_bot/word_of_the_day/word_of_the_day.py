#!/usr/bin/env python3
import feedparser

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import DBHelper

DATABASE = get_abs_path(__file__, 'word_of_the_day.db')
db = DBHelper(DATABASE)
FEED_URL = 'http://www.macmillandictionary.com/wotd/wotdrss.xml'


class WordOfTheDayBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(WordOfTheDayBot, self).__init__(*args, **kwargs)

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

            self.update_status(status)

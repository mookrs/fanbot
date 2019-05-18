#!/usr/bin/env python3
import time

import feedparser

from ..basebot import BaseBot, get_abs_path
from ..db import Database

DATABASE = get_abs_path(__file__, 'jandan.db')
db = Database(DATABASE)
FEED_URL = 'http://jandan.net/feed'


class Bot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def https_to_http(self, link):
        if link[4] == 's':
            return link[0:4] + link[5:]
        return link

    def replace_danger_words(self, s):
        return s.replace('强奸', '强*')

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS jandan (`guid`, `url`, `title`, `date_added`)')

        parsed_feed = feedparser.parse(FEED_URL)
        for entry in reversed(parsed_feed.entries):
            record = db.query('SELECT * FROM jandan WHERE guid=?', (entry.guid,))
            if not record:
                link = self.https_to_http(entry.link)
                title = entry.title

                data = (entry.guid, link, title, time.strftime(
                    '%Y-%m-%d %H:%M:%S', entry.updated_parsed))
                db.execute(
                    'INSERT INTO jandan (`guid`, `url`, `title`, `date_added`) VALUES (?,?,?,?)', data)
                db.commit()

                description = entry.description
                description = self.replace_danger_words(description)
                title = self.replace_danger_words(title)

                status = '【{}】{} {}'.format(title, link, description)
                self.update_status(status)

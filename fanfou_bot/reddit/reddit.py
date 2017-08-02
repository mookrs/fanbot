#!/usr/bin/env python3
import praw

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import DBHelper
from ..settings import RedditClientId, RedditClientSecret, RedditUserAgent

DATABASE = get_abs_path(__file__, 'reddit.db')
db = DBHelper(DATABASE)


class RedditBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(RedditBot, self).__init__(*args, **kwargs)

    def fetch_preview_img(self, preview_img_url):
        return None if preview_img_url is None else self.open_url(preview_img_url).read()

    def process_submission(self, submission):
        record = db.query('SELECT * FROM reddit WHERE id=?', (submission.id,))

        if not record:
            data = (submission.id, submission.title)
            db.execute('INSERT INTO reddit (`id`, `title`) VALUES (?,?)', data)
            db.commit()

            preview_img_url = submission.preview['images'][0]['source']['url'] if hasattr(submission, 'preview') else None

            if submission.url.endswith(('.jpg', '.png', '.gif', 'gifv')):
                submission_img_url = submission.url[:-1] if submission.url.endswith('gifv') else submission.url

                response = self.open_url(submission_img_url)

                if self.accepted_img_size(response):
                    submission_url = ''
                    photo = response.read()
                else:
                    submission_url = self.shorten_url(submission.url) + ' '
                    photo = self.fetch_preview_img(preview_img_url)
            else:
                submission_url = self.shorten_url(submission.url) + ' '
                photo = self.fetch_preview_img(preview_img_url)

            status = '[{}] {}{}'.format(
                submission.subreddit.display_name, submission_url, submission.title)

            chunks = self.get_chunks(status)
            for chunk in chunks[:-1]:
                self.update_status(chunk)
            self.update_status(chunks[-1], photo=photo)

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS reddit (`id`, `title`)')

        reddit = praw.Reddit(client_id=RedditClientId,
                             client_secret=RedditClientSecret,
                             user_agent=RedditUserAgent)

        for submission in reddit.front.hot(limit=15):
            self.process_submission(submission)

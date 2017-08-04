#!/usr/bin/env python3
from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import DBHelper

DATABASE = get_abs_path(__file__, 'jandan_pic.db')
db = DBHelper(DATABASE)
PIC_URL = 'https://jandan.net/pic'


class JandanPicBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(JandanPicBot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(('User-agent', 'Mozilla/5.0'), ('Cookie', '458528247=db856X2bSPJdJD3mZ0qNgqHxstlcw%2BC4xtmr%2BPfjKA; jdna=596e6fb28c1bb47f949e65e1ae03f7f5#1466510995815'))

    def get_last_page(self):
        soup = self.make_soup(PIC_URL)
        span = soup.find('span', {'class': 'current-comment-page'})
        return int(span.get_text()[1:-1])

    def low_score(self, item):
        ooxx = item.find('div', {'class': 'jandan-vote'}, recursive=False).find_all('span')
        oo = int(ooxx[1].get_text())
        xx = int(ooxx[3].get_text())
        if oo < 15 or xx * 3 > oo:
            return True
        return False

    def process_page(self, page):
        page_url = '{}/page-{}'.format(PIC_URL, page)
        soup = self.make_soup(page_url, parser='lxml')

        items = soup.find_all('div', {'class': 'row'})
        for item in reversed(items):
            if self.low_score(item):
                continue

            item_content = item.find('div', {'class': 'text'}, recursive=False)
            item_id = item_content.span.a.get_text()
            record = db.query('SELECT * FROM pictrue WHERE id=?', (item_id,))
            if not record:
                text = item_content.p.get_text(strip=True).replace('[查看原图]', '')
                img_tags = item.find_all('a', {'class': 'view_img_link'}) or item.find_all('img')
                img_count = len(img_tags)

                for index, img_tag in enumerate(img_tags, start=1):
                    prefix = '' if img_count == 1 else '({}/{}) '.format(index, img_count)
                    status = prefix + text if index == 1 else prefix

                    img_url = img_tag.get('href') or img_tag.get('src')
                    if img_url.startswith('//'):
                        img_url = 'http:' + img_url

                    response = self.open_url(img_url, self.opener)
                    if not self.accepted_img_size(response):
                        status = status + ' ' + img_url
                        result = self.update_status(status)
                    else:
                        result = self.update_status(status, response.read())

                    status_id = result['id'] if result is not None else None

                    db.execute('INSERT INTO pictrue (`id`, `url`, `status_id`) VALUES (?,?,?)', (item_id, img_url, status_id))
                    db.commit()

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS pictrue (`id`, `url`, `status_id`)')

        last_page = self.get_last_page()
        for page in range(last_page - 1, last_page + 1):
            self.process_page(page)

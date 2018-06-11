#!/usr/bin/env python3
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import base64
import re

from hashlib import md5

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import Database

DATABASE = get_abs_path(__file__, 'jandan_pic.db')
db = Database(DATABASE)
PIC_URL = 'https://jandan.net/pic'
PATTERN_T = re.compile('f\.remove\(\);var c=.+?\(e,"(.+?)"\)')


class JandanPicBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(JandanPicBot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(
            ('User-agent', 'Mozilla/5.0'),
            ('Cookie', '__cfduid=d669a4b2c49aa6fc3759bab643098b8b21503417105')
        )
        self.t = ''

    def low_score(self, item):
        ooxx = item.find('div', {'class': 'jandan-vote'}, recursive=False).find_all('span')
        oo = int(ooxx[2].get_text())
        xx = int(ooxx[4].get_text())
        if oo < 15 or xx * 3 > oo:
            return True
        return False

    def add_http_scheme(self, url):
        if not url.startswith('http'):
            url = 'http:' + url
        return url

    def get_t(self, js_url):
        js = self.open_url(js_url, self.opener)
        t = PATTERN_T.search(js.read().decode()).group(1)
        return t

    def decrypt(self, n):
        # e = 0
        # r = 4
        # t = md5(self.t.encode()).hexdigest()
        d = n
        # p = md5(t[:16].encode()).hexdigest()
        # o = md5(t[16:].encode()).hexdigest()

        # m = n[:r]
        # c = p + md5((p + m).encode()).hexdigest()

        # n = n[r:]

        # l = base64.b64decode(n + (-len(n) % 4) * '=')

        # k = list(range(256))

        # b = [ord(c[h % len(c)]) for h in range(256)]

        # g = 0
        # for h in range(256):
        #     g = (g + k[h] + b[h]) & 0xFF
        #     k[g], k[h] = k[h], k[g]

        # u = ''
        # q = 0
        # g = 0
        # for h in l:
        #     q = (q + 1) & 0xFF
        #     g = (g + k[q]) & 0xFF
        #     k[g], k[q] = k[q], k[g]
        #     u += chr(int(h) ^ (k[(k[q] + k[g]) & 0xFF]))

        # u = u[26:]
        u = base64.b64decode(d + (-len(d) % 4) * '=').decode()  # Without `(-len(d) % 4) * '='` is also OK

        u = re.sub(r'(\/\/\w+\.sinaimg\.cn\/)(\w+)(\/.+\.(gif|jpg|jpeg))', r'\1large\3', u)
        u = self.add_http_scheme(u)
        return u

    def get_img_urls(self, img_hash_tags):
        img_urls = []
        for img_hash_tag in img_hash_tags:
            img_hash = img_hash_tag.extract().get_text()
            img_url = self.decrypt(img_hash)

            print(img_hash)
            img_urls.append(img_url)

        return img_urls

    def process_page(self, page):
        soup = self.make_soup(page, self.opener, parser='lxml')

        if not self.t:
            js_url = soup.find('script', {'src': lambda x: x and '//cdn.jandan.net/static/min/' in x})['src']
            js_url = self.add_http_scheme(js_url)
            self.t = self.get_t(js_url)

        items = soup.find_all('div', {'class': 'row'})
        for item in reversed(items):
            if self.low_score(item):
                continue

            item_content = item.find('div', {'class': 'text'}, recursive=False)
            item_id = item_content.span.a.get_text()
            record = db.query('SELECT * FROM pictrue WHERE id=?', (item_id,))
            if not record:
                img_hash_tags = item_content.find_all('span', {'class': 'img-hash'})
                img_urls = self.get_img_urls(img_hash_tags)
                img_count = len(img_urls)
                text = item_content.p.get_text(strip=True)

                for index, img_url in enumerate(img_urls, start=1):
                    prefix = '' if img_count == 1 else '({}/{}) '.format(index, img_count)
                    status = prefix + text if index == 1 else prefix

                    response = self.open_url(img_url, self.opener)
                    if not self.accepted_img_size(response):
                        status = status + ' ' + img_url
                        result = self.update_status(status)
                    else:
                        result = self.update_status(status, response.read(), timeout=15)

                    if result is not None:
                        db.execute('INSERT INTO pictrue (`id`, `url`, `status_id`) VALUES (?,?,?)', (item_id, img_url, result['id']))
                        db.commit()

        a_tag = soup.find('a', {'class': 'previous-comment-page'})
        next_page = self.add_http_scheme(a_tag['href'])
        return next_page

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS pictrue (`id`, `url`, `status_id`)')

        next_page = PIC_URL
        for _ in range(3):
            next_page = self.process_page(next_page)

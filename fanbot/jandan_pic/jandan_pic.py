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
PATTERN_X = re.compile('f\.remove\(\);var c=.+?\(e,"(.+?)"\)')


class JandanPicBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(JandanPicBot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(
            ('User-agent', 'Mozilla/5.0'),
            ('Cookie', '__cfduid=d669a4b2c49aa6fc3759bab643098b8b21503417105')
        )
        self.x = ''

    def get_x(self, js_url):
        js = self.open_url(js_url, self.opener)
        x = PATTERN_X.search(js.read().decode('utf-8')).group(1)
        return x

    def get_last_page(self):
        soup = self.make_soup(PIC_URL, self.opener)

        js_url = soup.find('script', {'src': lambda x: x and '//cdn.jandan.net/static/min/' in x})['src']
        if not js_url.startswith('http:'):
            js_url = 'http:' + js_url
        self.x = self.get_x(js_url)

        span = soup.find('span', {'class': 'current-comment-page'})
        return int(span.get_text()[1:-1])

    def low_score(self, item):
        ooxx = item.find('div', {'class': 'jandan-vote'}, recursive=False).find_all('span')
        oo = int(ooxx[2].get_text())
        xx = int(ooxx[4].get_text())
        if oo < 15 or xx * 3 > oo:
            return True
        return False

    def decrypt(self, n):
        g = 4
        x = md5(self.x.encode('utf-8')).hexdigest()
        w = md5(x[:16].encode('utf-8')).hexdigest()
        u = md5(x[16:].encode('utf-8')).hexdigest()

        t = n[:g]
        r = w + md5((w + t).encode('utf-8')).hexdigest()

        n = n[g:]
        m = base64.b64decode(n + (4 - len(n) % 4) * '=')

        h = list(range(256))
        q = [ord(r[i % 64]) for i in range(256)]
        o = 0
        for p in range(256):
            o = (o + h[p] + q[p]) & 0xFF
            h[p], h[o] = h[o], h[p]

        l = ''
        v = 0
        o = 0
        for p in m:
            v = (v + 1) & 0xFF
            o = (o + h[v]) & 0xFF
            h[v], h[o] = h[o], h[v]
            l += chr(int(p) ^ (h[(h[v] + h[o]) & 0xFF]))
        l = l[26:]
        if not l.startswith('http:'):
            l = 'http:' + l
        return l

    def get_img_urls(self, img_hash_tags):
        img_urls = []
        for img_hash_tag in img_hash_tags:
            img_hash = img_hash_tag.extract().get_text()
            img_url = self.decrypt(img_hash)

            img_url_parts = img_url.split('/')
            img_url_parts[3] = 'large'
            img_url = '/'.join(img_url_parts)

            img_urls.append(img_url)

        return img_urls

    def process_page(self, page):
        page_url = '{}/page-{}'.format(PIC_URL, page)
        soup = self.make_soup(page_url, self.opener, parser='lxml')

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

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS pictrue (`id`, `url`, `status_id`)')

        last_page = self.get_last_page()
        for page in range(last_page - 1, last_page + 1):
            self.process_page(page)

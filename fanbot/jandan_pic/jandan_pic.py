import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import Database

DATABASE = get_abs_path(__file__, 'jandan_pic.db')
db = Database(DATABASE)
PIC_URL = 'https://jandan.net/pic'


class JandanPicBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(JandanPicBot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(
            ('User-agent', 'Mozilla/5.0'),
            ('Cookie', '__cfduid=d669a4b2c49aa6fc3759bab643098b8b21503417105')
        )

    def low_score(self, item):
        ooxx = item.find('div', {'class': 'jandan-vote'}, recursive=False).find_all('span')
        oo = int(ooxx[2].get_text())
        xx = int(ooxx[4].get_text())
        if oo < 15 or xx * 3 > oo:
            return True
        return False

    def add_http_scheme(self, url):
        if not url.startswith('http:'):
            url = 'http:' + url
        return url

    def get_img_urls(self, img_tags):
        img_urls = []
        for img_tag in img_tags:
            img_url = img_tag.get('href') or img_tag.get('src')
            img_url = self.add_http_scheme(img_url)
            img_urls.append(img_url)
        return img_urls

    def process_page(self, page):
        soup = self.make_soup(page, self.opener, parser='lxml')

        items = soup.find_all('div', {'class': 'row'})
        for item in reversed(items):
            if self.low_score(item):
                continue

            item_content = item.find('div', {'class': 'text'}, recursive=False)
            item_id = item_content.span.a.get_text()
            record = db.query('SELECT * FROM pictrue WHERE id=?', (item_id,))
            if not record:
                img_tags = item_content.find_all('a', {'class': 'view_img_link'}) or item_content.find_all('img')
                img_urls = self.get_img_urls(img_tags)
                img_count = len(img_urls)
                text = item_content.p.get_text(strip=True).replace('[查看原图]', '')

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

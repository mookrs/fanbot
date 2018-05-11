#!/usr/bin/env python3
import json

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import Database

DATABASE = get_abs_path(__file__, 'photo_of_the_day.db')
db = Database(DATABASE)

BASE_URL = 'http://www.ngchina.com.cn'
API_IMG_LIST = 'http://www.ngchina.com.cn/index.php?a=loadmorebya&catid=39&modelid=3'


class PhotoOfTheDayBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(PhotoOfTheDayBot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(
            ('User-agent', 'Mozilla/5.0'),
            ('Cookie', '__cfduid=d5f95d969c7daf37541465d15f329b3221525791837')
        )

    def page_exist(self, page_url):
        record = db.query('SELECT * FROM pictrue WHERE page_url=?', (page_url,))
        return True if record else False

    def get_recent_page_info(self):
        response = self.open_url(API_IMG_LIST, self.opener)
        data = json.loads(response.read().decode('utf-8'))

        relative_url = data[0]['url']
        title = data[0]['title'][5:].strip()
        desc = data[0]['description']

        return BASE_URL + relative_url, title, desc

    def get_long_desc(self, article_con):
        if (article_con.div and article_con.div.get_text().strip() and
                not article_con.div.get_text().strip().startswith('摄影：') and
                (not article_con.div.has_attr('class') or
                    (article_con.div.has_attr('class') and
                     article_con.div['class'][0] != 'counsel'))):
            # 想获取的页面形如
            # http://www.ngchina.com.cn/photography/photo_of_the_day/5281.html
            # 需要排除的页面形如
            # <div>&nbsp;</div>
            # http://www.ngchina.com.cn/photography/photo_of_the_day/5288.html
            # <div class="counsel">
            # http://www.ngchina.com.cn/photography/photo_of_the_day/5127.html
            long_desc = article_con.div.get_text().strip()
        else:
            long_desc = article_con.get_text().strip().split('\n')[0]

        return long_desc

    def get_page_detail(self, page_url):
        soup = self.make_soup(page_url, self.opener)

        img_url = soup.find('div', {'class': 'tab_imgs'}).find('img').get('src')

        article_con = soup.find('div', {'class': 'article_con'})
        long_desc = self.get_long_desc(article_con)

        return img_url, long_desc

    def replace_redundant_words(self, old_status):
        new_status = old_status.replace('你来掌镜摄影师', '摄影师').replace('由你掌镜摄影师', '摄影师')
        return new_status

    def run(self):
        db.execute('CREATE TABLE IF NOT EXISTS pictrue (`page_url`, `img_url`)')

        page_url, title, short_desc = self.get_recent_page_info()
        if self.page_exist(page_url):
            return

        img_url, long_desc = self.get_page_detail(page_url)

        status = '【{}】{}'.format(title, long_desc)
        if len(status) > 140:
            status = '【{}】{}'.format(title, short_desc)
        status = self.replace_redundant_words(status)

        response = self.open_url(img_url, self.opener)
        result = self.update_status(status, photo=response.read(), timeout=30)

        # Saves to database
        if result:
            db.execute('INSERT INTO pictrue (`page_url`, `img_url`) VALUES (?,?)', (page_url, img_url))
            db.commit()

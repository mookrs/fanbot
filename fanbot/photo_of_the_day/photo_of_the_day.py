import json

from ..basebot import get_abs_path
from ..spiderbot import SpiderBot
from ..db import Database

DATABASE = get_abs_path(__file__, 'photo_of_the_day.db')
db = Database(DATABASE)

BASE_URL = 'http://www.ngchina.com.cn'
API_IMG_LIST = 'http://www.ngchina.com.cn/index.php?a=loadmorebya&catid=39&modelid=3'


class Bot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3642.0 Safari/537.36'),
            ('Cookie', '__cfduid=d106044aba80f86e5d8d1270c45ee78411559650908')
        )

    def replace_redundant_words(self, old_status):
        new_status = old_status.replace('你来掌镜摄影师', '摄影师').replace('由你掌镜摄影师', '摄影师').replace('Your Shot摄影师', '摄影师')
        return new_status

    def page_exist(self, page_url):
        record = db.query('SELECT * FROM pictrue WHERE page_url=?', (page_url,))
        return True if record else False

    def get_long_desc(self, article_con):
        # <div ...>[desc]</div> + <div>&nbsp;</div> + ...
        # http://www.ngchina.com.cn/photography/photo_of_the_day/5281.html
        # <div ...>[desc] <br> <br> 摄影：xxxx，你来掌镜YOURSHOT</div> + ...
        # http://www.ngchina.com.cn//photography/photo_of_the_day/5913.html#
        # [desc] + <div>&nbsp;</div> + ...
        # http://www.ngchina.com.cn/photography/photo_of_the_day/5288.html
        # [desc] <br> <br> 摄影：xxxx，你来掌镜YOURSHOT + ...
        # http://www.ngchina.com.cn//photography/photo_of_the_day/5908.html
        # <span ...>[desc]</span> + ...
        # http://www.ngchina.com.cn/photography/photo_of_the_day/5127.html
        long_desc = article_con.get_text().strip().split('\n')[0]
        return long_desc

    def get_page_detail(self, page_url):
        soup = self.make_soup(page_url, self.opener)

        img_url = soup.find('div', {'class': 'tab_imgs'}).find('img').get('src')

        article_con = soup.find('div', {'class': 'article_con'})
        long_desc = self.get_long_desc(article_con)

        return img_url, long_desc

    def get_recent_page_info(self):
        response = self.open_url(API_IMG_LIST, self.opener)
        data = json.loads(response.read().decode('utf-8'))

        relative_url = data[0]['url']
        title = data[0]['title'][5:].strip()
        desc = data[0]['description']

        return BASE_URL + relative_url, title, desc

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
        if result:
            db.execute('INSERT INTO pictrue (`page_url`, `img_url`) VALUES (?,?)', (page_url, img_url))
            db.commit()

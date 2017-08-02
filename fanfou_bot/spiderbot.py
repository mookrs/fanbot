import json

from urllib.error import URLError
from urllib.parse import quote
from urllib.request import build_opener, urlopen

from bs4 import BeautifulSoup

from .basebot import BaseBot

RETRY_TIMES = 2
RETRY_INTERVAL = 2
TIMEOUT = 15
API_TEMPLATE = 'http://api.t.sina.com.cn/short_url/shorten.json?source=2058402309&url_long={}'
_4MB = 4194304
_2MB = 2097152


class SpiderBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(SpiderBot, self).__init__(*args, **kwargs)

    def make_opener(self, *headers):
        opener = build_opener()
        opener.addheaders = []
        for header in headers:
            opener.addheaders.append(header)
        return opener

    def open_url(self, url, opener=None, retry_times=RETRY_TIMES, retry_interval=RETRY_INTERVAL, timeout=TIMEOUT):
        previous_retry_times = 0

        while True:
            try:
                if opener is None:
                    response = urlopen(url, timeout=timeout)
                else:
                    response = opener.open(url, timeout=timeout)
                break
            except URLError as e:
                self.logger.warning('Exception at:', url)
                self.logger.warning(e)
            except Exception as e:
                self.logger.warning('Exception at:', url)
                self.logger.warning(e)

            previous_retry_times += 1
            if previous_retry_times > retry_times:
                break

            time.sleep(retry_interval)
            continue

        return response

    def make_soup(self, url, opener=None, retry_times=RETRY_TIMES, retry_interval=RETRY_INTERVAL, timeout=TIMEOUT, parser='html.parser'):
        html = self.open_url(url, opener, retry_times, retry_interval, timeout)
        return BeautifulSoup(html, parser)

    def shorten_url(self, url_long):
        api = API_TEMPLATE.format(quote(url_long, safe=':/'))
        response = self.open_url(api)
        data = json.loads(response.read().decode('utf-8'))
        url_short = data[0]['url_short']
        return url_short

    def accepted_img_type(self, mime, *img_types):
        return any(img_type == mime for img_type in img_types)

    def accepted_img_size(self, response):
        mime = response.info()['Content-Type']
        img_size = int(response.info()['Content-Length'])

        if (self.accepted_img_type(mime, 'jpeg', 'png') and img_size <= _4MB) or (self.accepted_img_type(mime, 'gif') and img_size <= _2MB):
            return True

        return False

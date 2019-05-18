#!/usr/bin/env python3
import json
import time
from urllib.request import quote

from ..spiderbot import SpiderBot


class Bot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3269.3 Safari/537.36'))

    def fetch_page(self):
        # See https://zh.moegirl.org/api.php?action=help&modules=query%2Brandom
        # rnnamespace: 只返回这些名字空间的页面
        api_random_page = 'https://zh.moegirl.org/api.php?action=query&list=random&rnnamespace=0&format=json'
        response = self.open_url(api_random_page)
        data = json.loads(response.read().decode('utf-8'))

        page_id = data['query']['random'][0]['id']
        page_title = data['query']['random'][0]['title']
        return page_id, page_title

    def fetch_summary(self, page_url):
        soup = self.make_soup(page_url, self.opener, parser='lxml')
        summary = ''

        if page_url.startswith('https://zh.moegirl.org/%E6%88%98%E8%88%B0%E5%B0%91%E5%A5%B3:'):
            # `战舰少女` 专题
            summary = soup.find('div', 'infotemplatebox').find_next_sibling('p').get_text(strip=True)
        elif soup.find(['div', 'table'], id='disambigbox'):
            # 消歧页去掉摘要
            pass
        else:
            paragraphs = soup.find(id='mw-content-text').find_all('p', recursive=False)
            for paragraph in paragraphs:
                summary = paragraph.get_text(strip=True)
                if summary and not summary.startswith('window.RLQ'):
                    break

        return summary

    def fetch_image(self, page_id):
        api_page_image = 'https://zh.moegirl.org/api.php?action=query&pageids={}&prop=pageimages&pithumbsize=500&format=json'.format(page_id)
        response = self.open_url(api_page_image)
        data = json.loads(response.read().decode('utf-8'))

        page_infos = data['query']['pages'][str(page_id)]
        thumbnail = page_infos.get('thumbnail')
        if thumbnail is not None:
            thumbnail_source = thumbnail['source']
            thumbnail_response = self.open_url(thumbnail_source, self.opener)
            return thumbnail_response.read() if thumbnail_response is not None else None

        return None

    def run(self):
        page_id, page_title = self.fetch_page()

        page_url = 'https://zh.moegirl.org/{}'.format(quote(page_title, safe='/:'))
        page_summary = self.fetch_summary(page_url)

        status = '【{}】{} {}'.format(page_title, page_url, page_summary)

        page_image = self.fetch_image(page_id)
        self.update_status(status, photo=page_image)

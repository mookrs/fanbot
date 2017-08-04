#!/usr/bin/env python3
import json
import time
from urllib.request import quote

from ..spiderbot import SpiderBot

API_RANDOM_PAGE = 'https://zh.moegirl.org/api.php?format=json&action=query&list=random&rnnamespace=0&rnlimit=1&continue='


class MoegirlDailyBot(SpiderBot):
    def __init__(self, *args, **kwargs):
        super(MoegirlDailyBot, self).__init__(*args, **kwargs)
        self.opener = self.make_opener(('User-agent', 'Mozilla/5.0'))

    def fetch_page(self):
        response = self.open_url(API_RANDOM_PAGE)
        data = json.loads(response.read().decode('utf-8'))
        page_id = data['query']['random'][0]['id']
        page_title = data['query']['random'][0]['title']
        return page_id, page_title

    def fetch_summary(self, page_url):
        # Use lxml instead of default html parser will get better soup
        soup = self.make_soup(page_url, self.opener, parser='lxml')
        summary = ''

        # 处理「战舰少女」专题
        if page_url.startswith('https://zh.moegirl.org/%E6%88%98%E8%88%B0%E5%B0%91%E5%A5%B3:'):
            summary = soup.find('div', {'class': 'infotemplatebox'}).find_next_sibling('p').get_text(strip=True)
        # 消歧页去掉摘要
        elif soup.find(['div', 'table'], {'id': 'disambigbox'}):
            pass
        # 正常情况
        else:
            contents = soup.find('div', {'id': 'mw-content-text'}).find_all('p', recursive=False)
            for content in contents:
                summary = content.get_text(strip=True)
                if summary:
                    if summary.startswith('.bilibili-video-button'):
                        summary = ''
                    break

        return summary

    def fetch_image(self, page_id):
        api_page_image = 'https://zh.moegirl.org/api.php?format=json&action=query&pageids={}&prop=pageimages&pithumbsize=500'.format(page_id)
        response = self.open_url(api_page_image, self.opener)
        data = json.loads(response.read().decode('utf-8'))

        page_infos = data['query']['pages'][str(page_id)]
        thumbnail = page_infos.get('thumbnail')
        if thumbnail is not None:
            thumbnail_source = page_infos['thumbnail']['source']
            thumbnail_response = self.open_url(thumbnail_source)
            return thumbnail_response.read() if thumbnail_response is not None else None

        return None

    def run(self):
        page_id, page_title = self.fetch_page()

        page_url = 'https://zh.moegirl.org/{}'.format(quote(page_title, safe='/:'))

        # Avoid HTTP Error 429: Too Many Requests
        time.sleep(30)
        page_summary = self.fetch_summary(page_url)
        if len(page_url) >= 40:
            page_url = self.shorten_url(page_url)

        status = '【{}】{} {}'.format(page_title, page_url, page_summary)

        time.sleep(60)
        page_image = self.fetch_image(page_id)
        self.update_status(status, photo=page_image)

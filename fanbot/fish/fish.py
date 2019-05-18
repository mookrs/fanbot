#!/usr/bin/env python3
import calendar
import datetime
import pickle
import os
import random
import re
import time

from collections import deque

from ..basebot import BaseBot, get_abs_path

pattern = re.compile(r'^@\S+\s([\s\S]+)$')


class Bot(BaseBot):
    zh_weekday = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
    emoji_int_dict = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣'}

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def get_greeting(self, now):
        hour = now.strftime('%H')
        if hour in ['01', '02', '03', '04', '05']:
            pre_g = '凌晨好，'
            if now.isoweekday() in [1, 2, 3, 4, 5]:
                post_g = '生生不息，摸鱼不止。在这万籁俱寂的凌晨，众生都已睡去，是什么放不下的牵挂，让你还在摸鱼？'
            else:
                post_g = '生生不息，摸鱼不止。一周之末的凌晨，是摸鱼者的狂欢之时！'
        elif hour in ['06', '07', '08', '09']:
            pre_g = '早安，'
            if now.isoweekday() in [1, 2, 3, 4, 5]:
                post_g = '生生不息，摸鱼不止。早起的人儿有鱼摸。'
            else:
                post_g = '生生不息，摸鱼不止。周末的清晨，早早醒来，抿一口茶，摸着鱼，望众生苏醒，何等享受。'
        elif hour in ['10', '11']:
            pre_g = '上午好，'
            post_g = '生生不息，摸鱼不止。'
        elif hour in ['12', '13']:
            pre_g = '中午好，'
            post_g = '生生不息，摸鱼不止。'
        elif hour in ['14', '15', '16', '17']:
            pre_g = '下午好，'
            post_g = '生生不息，摸鱼不止。'
        elif hour in ['18', '19', '20', '21', '22']:
            pre_g = '晚上好，'
            post_g = '生生不息，摸鱼不止。人要懂得劳逸结合，摸鱼一天了，应该摸鱼休息一下。'
        elif hour in ['23', '00']:
            pre_g = '深夜好，'
            post_g = '生生不息，摸鱼不止。'

        return pre_g, post_g

    def get_week_postion(self, weekday_left, weekend_left):
        week_postion = ''
        if weekday_left < 49 and weekday_left > 0:
            week_postion = '\n还有{}小时，周末就到了。'.format(weekday_left)
        elif weekend_left < 11:
            week_postion = '\n还有{}小时，周末就结束了。'.format(weekend_left)
        return week_postion

    def command_now(self, mention):
        now = datetime.datetime.now()
        pre_g, post_g = self.get_greeting(now)

        month_len = calendar.monthrange(now.year, now.month)[1]
        year_len = 366 if calendar.isleap(now.year) else 365

        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daypass = (now - midnight).seconds

        # 本来用于提示「还有{}天，今年就结束了。」
        # 因为 140 字限制省略
        year_left = year_len - now.timetuple().tm_yday
        month_left = month_len - now.day
        weekday_left = 120 - ((now.isoweekday() - 1) * 24 + now.hour)
        weekend_left = 48 + weekday_left

        is_global_status = False
        if random.random() < 0.85:
            reply_to_user = '@{} '.format(mention['user']['screen_name'])
        else:
            reply_to_user = ''
            is_global_status = True

        status = '{}{}现在是{}。\n\n这一天已经过去了{}%。\n这一周已经过去了{}%。\n这个月已经过去了{}%。{}\n\n{}'.format(
            reply_to_user,
            pre_g,
            now.strftime('%Y年%m月%d日，星期{}，%H:%M').format(self.zh_weekday[now.isoweekday()]),
            daypass // 864,
            ((now.isoweekday() - 1) * 86400 + daypass) // 6048,
            ((now.day - 1) * 86400 + daypass) // (month_len * 864),
            self.get_week_postion(weekday_left, weekend_left),
            post_g)

        if is_global_status:
            result = self.update_status(status)
        else:
            result = self.update_status(status, in_reply_to_status_id=mention['id'])

        return result

    def command_roll(self, mention):
        emoji_dice = '🎲'
        emoji_int = self.emoji_int_dict[random.randint(1, 6)]
        status = '@{} {}{}'.format(mention['user']['screen_name'], emoji_dice, emoji_int)
        result = self.update_status(status, in_reply_to_status_id=mention['id'])
        return result

    def handle_mention(self, mention):
        match = re.search(pattern, mention['text'])
        command = match.group(1).strip() if match else None

        if command == 'now':
            result = self.command_now(mention)
        elif command == 'roll':
            result = self.command_roll(mention)
        else:
            result = ''

        return result

    def run(self):
        pass

    def start(self):
        # If some mentions are deleted, handled mentions will be handled again.
        # So make handled_mentions bigger than the count of get_mentions().
        handled_mentions_file = get_abs_path(__file__, 'handled_mentions.p')
        handled_mentions = pickle.load(open(handled_mentions_file, 'rb')) if os.path.isfile(handled_mentions_file) else deque(maxlen=80)

        while True:
            # If failed to get mentions will return None
            mentions = self.get_mentions(count=20)
            reversed_mentions = reversed(mentions) if mentions is not None else []
            for mention in reversed_mentions:
                if mention['id'] in handled_mentions:
                    continue
                handled_mentions.append(mention['id'])

                result = self.handle_mention(mention)

                # Failed updating status, remove the failed mention
                if result is None:
                    handled_mentions.pop()

            pickle.dump(handled_mentions, open(handled_mentions_file, 'wb'))
            time.sleep(30)

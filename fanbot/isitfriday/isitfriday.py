#!/usr/bin/env python3
import datetime
import json
import os
import random

from ..basebot import BaseBot, get_abs_path


class IsItFridayBot(BaseBot):
    now = datetime.datetime.now()
    weekday = str(now.isoweekday())
    date = now.strftime('%Y%m%d')

    def __init__(self, *args, **kwargs):
        super(IsItFridayBot, self).__init__(*args, **kwargs)

    def load_profile(self):
        with open(get_abs_path(__file__, 'profile.json')) as f:
            profile = json.load(f)
        return profile

    def read_image(self, image_path):
        abs_image_path = get_abs_path(__file__, image_path)
        with open(abs_image_path, 'rb') as f:
            return f.read()

    def get_random_image(self, top):
        abs_top = get_abs_path(__file__, top)
        images = []
        for root, _, files in os.walk(abs_top):
            for file in files:
                images.append(os.path.join(root, file))
        return random.choice(images)

    def get_image_data(self, info):
        image_type = info.get('image_type')
        if image_type == 'false':
            image_path = self.get_random_image('false')
        elif image_type == 'true':
            image_path = self.get_random_image('true')
        elif image_type == 'custom':
            image_path = info['image_path']
        else:
            return None

        image_data = self.read_image(image_path)
        return image_data

    def run(self):
        profile = self.load_profile()
        info = profile[self.date] if self.date in profile else profile[self.weekday]

        status = random.choice(info['statuses'])
        image_data = self.get_image_data(info)

        self.update_status(status=status, photo=image_data)

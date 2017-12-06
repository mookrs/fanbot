#!/usr/bin/env python3
import datetime
import json
import os
import random

from ..basebot import BaseBot, get_abs_path


class IsItFridayBot(BaseBot):
    today = datetime.datetime.now().isoweekday()

    def __init__(self, *args, **kwargs):
        super(IsItFridayBot, self).__init__(*args, **kwargs)

    def get_status(self):
        with open(get_abs_path(__file__, 'statuses.json')) as statuses_file:
            statuses = json.load(statuses_file)
        return random.choice(statuses[str(self.today)])

    def get_img_path(self, top):
        images = []
        for root, dirs, files in os.walk(top):
            for file in files:
                images.append(os.path.join(root, file))
        return random.choice(images)

    def get_random_img(self, dir_name):
        image = self.get_img_path(get_abs_path(__file__, dir_name))
        with open(image, 'rb') as imagefile:
            return imagefile.read()

    def run(self, special_image=False, status=None):
        status = self.get_status() if status is None else status

        if special_image:
            imagedata = self.get_random_img('special')
        elif self.today == 5:
            imagedata = self.get_random_img('true')
        else:
            imagedata = self.get_random_img('false')

        self.update_status(status=status, photo=imagedata)

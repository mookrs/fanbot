import os
import time

from urllib.error import HTTPError, URLError

from fanpy.api import Fanfou, FanfouHTTPError
from fanpy.oauth import OAuth, read_token_file


class BaseBot(object):
    def __init__(self, consumer_key, consumer_secret,
                 fanfou_creds='token', index_file='index.txt'):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.fanfou_creds = fanfou_creds
        self.index_file = index_file
        self.fanfou = self._init_fanfou()

    def _init_fanfou(self):
        oauth_token, oauth_token_secret = read_token_file(self.fanfou_creds)
        return Fanfou(auth=OAuth(
            oauth_token, oauth_token_secret, self.consumer_key, self.consumer_secret))

    def _get_current_index(self):
        if not os.path.isfile(self.index_file):
            return 1
        with open(self.index_file) as f:
            return int(f.read().strip())

    def _increase_index(self, current_index):
        with open(self.index_file, 'w') as f:
            f.write(str(current_index + 1))

    def get_chunks(self, status, separtor='...'):
        """
            chunks = [chunk, chunk, ...]
            chunk = status_slice + separtor
        """
        slice_length = 140 - len(separtor)
        chunks = []
        # Break up the current status into chunks
        while len(status) > 140:
            status_slice = status[:slice_length]
            chunk = status_slice + separtor
            chunks.append(chunk)
            status = status[slice_length:]

        # When status is less than 140, add it to the list of chunks
        chunks.append(status)
        return chunks

    def update_status(self, status, imagedata=None, retry_times=2, retry_interval=2):
        has_retry = 0
        final_status = status
        while True:
            try:
                if imagedata is not None:
                    self.fanfou.photos.upload(photo=imagedata, status=final_status)
                else:
                    self.fanfou.statuses.update(status=final_status)
                break
            except FanfouHTTPError as e:
                # Duplicated status
                if e.e.code == 400:
                    final_status += '.'

                has_retry += 1
                if has_retry > retry_times:
                    break

                time.sleep(retry_interval)
                continue
            except Exception as e:
                # TimeoutError: [Errno 110] Connection timed out
                has_retry += 1
                if has_retry > retry_times:
                    break

                time.sleep(retry_interval)
                continue

    def destroy_status(self, is_latest=True, id=None):
        try:
            if is_latest:
                latest_status = self.fanfou.statuses.user_timeline(count=1)[0]
                latest_status_id = latest_status['id']
                self.fanfou.statuses.destroy(_id=latest_status_id)
            else:
                if id is not None:
                    self.fanfou.statuses.destroy(_id=id)
        except Exception as e:
            raise e

    def start(self):
        pass

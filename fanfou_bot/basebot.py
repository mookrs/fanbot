import logging
import os
import time

from abc import ABC, abstractmethod
from urllib.error import HTTPError, URLError

from fanpy.api import Fanfou, FanfouHTTPError
from fanpy.oauth import OAuth, read_token_file

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    def __init__(self, consumer_key, consumer_secret,
                 creds_file='token', index_file='index.txt',
                 logging_level=logging.WARNING):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.creds_file = creds_file
        self.index_file = index_file
        self.fanfou = self._init_fanfou()

        logger.setLevel(logging_level)

    def _init_fanfou(self):
        oauth_token, oauth_token_secret = read_token_file(self.creds_file)
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

    def get_chunks(self, status, separtor='...', chunk_length=140):
        slice_length = chunk_length - len(separtor)

        chunks = []
        while len(status) > chunk_length:
            status_slice = status[:slice_length]
            chunk = status_slice + separtor
            chunks.append(chunk)
            status = status[slice_length:]
        chunks.append(status)

        return chunks

    def update_status(self, status, imagedata=None,
                      in_reply_to_status_id=None, in_reply_to_user_id=None,
                      repost_status_id=None,
                      retry_times=2, retry_interval=2):
        previous_retry_times = 0
        final_status = status

        while True:
            try:
                if imagedata is not None:
                    self.fanfou.photos.upload(
                        photo=imagedata,
                        status=final_status,
                        in_reply_to_status_id=in_reply_to_status_id,
                        in_reply_to_user_id=in_reply_to_user_id,
                        repost_status_id=repost_status_id)
                else:
                    self.fanfou.statuses.update(
                        status=final_status,
                        in_reply_to_status_id=in_reply_to_status_id,
                        in_reply_to_user_id=in_reply_to_user_id,
                        repost_status_id=repost_status_id)
                break
            except FanfouHTTPError as e:
                if e.e.code == 400:
                    logger.warning('Duplicated status: {}'.format(final_status))
                    final_status += '.'
                else:
                    logger.warning(e)
            except Exception as e:
                logger.warning(e)

            previous_retry_times += 1
            if previous_retry_times > retry_times:
                break

            time.sleep(retry_interval)
            continue

    def destroy_status(self, id=None, retry_times=0, retry_interval=2):
        """
            If id is None, then deletes the latest status
        """
        previous_retry_times = 0

        while True:
            try:
                if id is None:
                    latest_status_id = self.fanfou.statuses.user_timeline(count=1)[0]['id']
                    self.fanfou.statuses.destroy(_id=latest_status_id)
                else:
                    self.fanfou.statuses.destroy(_id=id)
                break
            except FanfouHTTPError as e:
                if e.e.code == 404:
                    logger.warning('There is no message: {}'.format(id))
                else:
                    logger.warning(e)
            except Exception as e:
                logger.warning(e)

            previous_retry_times += 1
            if previous_retry_times > retry_times:
                break

            time.sleep(retry_interval)
            continue

    def get_mentions(self, since_id=None, max_id=None, count=None, page=None, mode=None):
        """
            If service is unstable, here also can retry
        """
        try:
            return self.fanfou.statuses.mentions(
                since_id=since_id, max_id=max_id, count=count, page=page, mode=mode)
        except Exception as e:
            # Will return None
            logger.warning(e)

    @abstractmethod
    def make_status(self):
        pass

    @abstractmethod
    def start(self):
        pass

import logging
import os
import sys
import time
from abc import ABC, abstractmethod
from urllib.error import HTTPError, URLError

from fanpy.api import Fanfou, FanfouHTTPError
from fanpy.oauth import OAuth, read_token_file

from .settings import ConsumerKey, ConsumerSecret

RETRY_TIMES = 2
RETRY_INTERVAL = 2
TIMEOUT = 10


def get_abs_path(module_file, path):
    return os.path.join(os.path.dirname(os.path.abspath(module_file)), path)


class BaseBot(ABC):
    def __init__(self, consumer_key=ConsumerKey, consumer_secret=ConsumerSecret,
                 creds_file='token', index_file='index.txt',
                 logging_level=logging.WARNING):
        child_module_name = self.__module__
        child_cls_dir = os.path.dirname(sys.modules[child_module_name].__file__)

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.creds_file = os.path.join(child_cls_dir, creds_file)
        self.index_file = os.path.join(child_cls_dir, index_file)
        self.fanfou = self._init_fanfou()
        self.logger = self._init_logger(child_module_name, logging_level)

    def _init_fanfou(self):
        oauth_token, oauth_token_secret = read_token_file(self.creds_file)
        return Fanfou(auth=OAuth(
            oauth_token, oauth_token_secret, self.consumer_key, self.consumer_secret))

    def _init_logger(self, child_module_name, logging_level):
        logger = logging.getLogger(child_module_name)
        logger.setLevel(logging_level)

        sh = logging.StreamHandler()
        sh.setLevel(logging_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        sh.setFormatter(formatter)

        logger.addHandler(sh)

        return logger

    def _get_current_index(self):
        if not os.path.isfile(self.index_file):
            return 1

        with open(self.index_file) as f:
            return int(f.read().strip())

    def _set_next_index(self, current_index, max_index=None):
        if max_index is not None and current_index == max_index:
            next_index = 1
        else:
            next_index = current_index + 1

        with open(self.index_file, 'w') as f:
            f.write(str(next_index))

    def get_chunks(self, status, separtor='...', chunk_length=140, is_reversed=True):
        slice_length_1x = chunk_length - len(separtor)
        slice_length_2x = chunk_length - len(separtor) * 2

        chunks = []
        if len(status) <= chunk_length:
            chunks.append(status)
        else:
            status_slice = status[:slice_length_1x]
            chunk = status_slice + separtor
            chunks.append(chunk)
            status = status[slice_length_1x:]
            while len(status) > slice_length_1x:
                status_slice = status[:slice_length_2x]
                chunk = separtor + status_slice + separtor
                chunks.append(chunk)
                status = status[slice_length_2x:]
            chunks.append(separtor + status)

        if is_reversed:
            chunks.reverse()

        return chunks

    def update_status(self, status, photo=None,
                      in_reply_to_status_id=None, in_reply_to_user_id=None,
                      repost_status_id=None,
                      retry_times=RETRY_TIMES, retry_interval=RETRY_INTERVAL,
                      timeout=TIMEOUT):
        previous_retry_times = 0
        final_status = status

        while True:
            try:
                if photo is not None:
                    return self.fanfou.photos.upload(
                        photo=photo,
                        status=final_status,
                        in_reply_to_status_id=in_reply_to_status_id,
                        in_reply_to_user_id=in_reply_to_user_id,
                        repost_status_id=repost_status_id,
                        _timeout=timeout)
                else:
                    return self.fanfou.statuses.update(
                        status=final_status,
                        in_reply_to_status_id=in_reply_to_status_id,
                        in_reply_to_user_id=in_reply_to_user_id,
                        repost_status_id=repost_status_id,
                        _timeout=timeout)
            except FanfouHTTPError as e:
                if e.e.code == 400:
                    # Won't log empty status for pic bot
                    if final_status:
                        self.logger.warning('Duplicated status: {}'.format(final_status))
                    final_status += '.'
                elif e.e.code == 500:
                    # HACK: API responses 500 sometimes successed
                    break
                else:
                    self.logger.warning('Exception when updating status')
                    self.logger.warning(e)
            except Exception as e:
                self.logger.warning('Exception when updating status')
                self.logger.warning(e)

            previous_retry_times += 1
            if previous_retry_times > retry_times:
                break

            time.sleep(retry_interval)

    def destroy_status(self, id=None,
                       retry_times=RETRY_TIMES, retry_interval=RETRY_INTERVAL,
                       timeout=TIMEOUT):
        """
            If id is None, then deletes the latest status
        """
        previous_retry_times = 0

        while True:
            try:
                if id is None:
                    id = self.fanfou.statuses.user_timeline(count=1, _timeout=timeout)[0]['id']
                self.fanfou.statuses.destroy(_id=id, _timeout=timeout)
                break
            except FanfouHTTPError as e:
                if e.e.code == 404:
                    self.logger.warning('There is no message: {}'.format(id))
                else:
                    self.logger.warning('Exception when destroying status')
                    self.logger.warning(e)
            except Exception as e:
                self.logger.warning('Exception when destroying status')
                self.logger.warning(e)

            previous_retry_times += 1
            if previous_retry_times > retry_times:
                break

            time.sleep(retry_interval)
            continue

    def get_mentions(self, since_id=None, max_id=None,
                     count=None, page=None, mode=None,
                     retry_times=RETRY_TIMES, retry_interval=RETRY_INTERVAL,
                     timeout=TIMEOUT):
        """
            Default count is 60
        """
        previous_retry_times = 0

        while True:
            try:
                if since_id is None:
                    return self.fanfou.statuses.mentions(
                        max_id=max_id, count=count, page=page, mode=mode, _timeout=timeout)
                else:
                    return self.fanfou.statuses.mentions(
                        since_id=since_id, max_id=max_id, count=count, page=page, mode=mode, _timeout=timeout)
                break
            except Exception as e:
                # Will return None
                self.logger.warning('Exception when getting mentions')
                self.logger.warning(e)

            previous_retry_times += 1
            if previous_retry_times > retry_times:
                break

            time.sleep(retry_interval)
            continue

    @abstractmethod
    def run(self):
        pass

    def start(self):
        pass

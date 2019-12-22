# -*- coding: utf-8 -*-

import os
import redis
from ohmyrss.settings import REDIS_FEED_DB, REDIS_HOST, REDIS_PORT
import time
from random import seed
from random import random


R = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_FEED_DB, decode_responses=True)
CRAWL_PREFIX = 'CRAWL/'


def mkdir(directory):
    return os.makedirs(directory, exist_ok=True)


def is_crawled_url(url):
    if R.get(CRAWL_PREFIX + url):
        return True
    return False


def mark_crawled_url(*urls):
    # both set before and after redirect url
    for url in urls:
        R.set(CRAWL_PREFIX + url, 1)


def current_ts():
    #seed(1000)
    rannum=random()
    current_ts=int(time.time()*rannum)

    return current_ts

# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: redis_conn.py
@time: 2020-03-20 12:01:09
@projectExplain: 
"""

import copy
from redis import StrictRedis
from dynaconf import settings

REDIS_CONF = settings.redis

redis_conn_instances = {}


def get_spider_redis_conn(db=settings.REDIS_DB):
    if db not in redis_conn_instances:
        config = copy.copy(REDIS_CONF)
        config['db'] = db
        redis_conn_instances[db] = StrictRedis(**config, decode_responses=True)
    return redis_conn_instances[db]


def get_pika_conn(config: dict = settings.pika):
    return StrictRedis(**config, decode_responses=True)

# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: utils.py
@time: 2020-11-03 12:06:30
@projectExplain: 
"""
from urllib.parse import urlparse, quote

from redis import StrictRedis
from pymongo import MongoClient
from sqlalchemy import create_engine

from common_servers.conf import ENV, ENV_PROD, MYSQL_READ_PRODUCT, consul_settings as settings


def url_scheme_checker(url, header='https'):
    """检查url的scheme 返回调整后的url"""
    if not url:
        return url
    par = urlparse(url)
    new_url = url
    if not par.scheme:
        url_replaced = par._replace(scheme=header)
        new_url = url_replaced.geturl()
        if '///' in new_url:
            new_url = new_url.replace('///', '//')
    elif "http" == par.scheme:
        url_replaced = par._replace(scheme=header)
        new_url = url_replaced.geturl()
    return new_url


def mongo_init_shard(client, db_name: str, col_name: str, shard_key: dict = {'_id': 'hashed'}):
    '''
    创建索引和分片
    :param client:
    :param db_name:
    :param col_name:
    :param shard_key:
    :return:
    '''
    db = client[db_name]
    col = db[col_name]

    if ENV == ENV_PROD:
        client.admin.command('enableSharding', db_name)
        is_sharded = db.command("collstats", col_name)['sharded']
        # 分片
        if not is_sharded:
            client.admin.command('shardCollection', f'{db_name}.{col_name}', key=shard_key)

    return col


def connect_mysql_engine(db='product'):
    MYSQL_READ_PRODUCT['db'] = db
    engine = create_engine(
        "mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8&autocommit=true".format(
            **MYSQL_READ_PRODUCT),
        pool_pre_ping=True, pool_recycle=3600, pool_size=20)
    return engine


def mongo_init_shard(client, db_name: str, col_name: str, shard_key: dict = {'_id': 'hashed'}):
    '''
    创建索引和分片
    :param client:
    :param db_name:
    :param col_name:
    :param shard_key:
    :return:
    '''
    db = client[db_name]
    col = db[col_name]

    client.admin.command('enableSharding', db_name)

    is_sharded = db.command("collstats", col_name)['sharded']
    # 分片
    if not is_sharded:
        client.admin.command('shardCollection', f'{db_name}.{col_name}', key=shard_key)

    return col


def connect_mongo(config: dict = settings.mongodb['high_mongo']):
    '''
    切换自建mongodb集群使用
    :param config:
    :return:
    '''
    mongo_client = MongoClient(config['ips'])
    if config['user']:
        mongo_client.admin.authenticate(config['user'], config['password'])
    return mongo_client


redis_instances = {}


def get_redis_conn(db=0):
    REDIS_CONF = {
        "host": settings.redis['host'],
        "port": settings.redis['port'],
        "db": db,
        "password": settings.redis['password']
    }
    if db not in redis_instances:
        REDIS_CONF["db"] = db
        ins = StrictRedis(**REDIS_CONF, decode_responses=True)
        redis_instances[db] = ins
    return redis_instances[db]


def deal_chinese_num(num_str: str):
    if not num_str: return 0
    if num_str.isdigit():
        return int(num_str)
    elif '万' in num_str:
        return int(float(num_str.replace('万', '').replace('+', '')) * 10000)
    elif 'k' in num_str:
        return int(float(num_str.replace('k', '').replace('+', '')) * 1000)
    elif 'K' in num_str:
        return int(float(num_str.replace('K', '').replace('+', '')) * 1000)
    elif '千' in num_str:
        return int(float(num_str.replace('千', '').replace('+', '')) * 1000)
    elif '+' in num_str:
        return int(float(num_str.replace('+', '')))
    else:
        return 0


def _encode_url(url: str, data) -> str:
    '''
    :param url:
    :param data: 支持元祖 字典
    :return:
    '''
    result = []
    to_list = list(data.items()) if type(data) == dict else list(data)
    for k, vs in to_list:
        if isinstance(vs, (str, bytes)) or not hasattr(vs, '__iter__'):
            vs = [vs]
        for v in vs:
            if v is not None:
                result.append(
                    (k.encode('utf-8') if isinstance(k, str) else k,
                     v.encode('utf-8') if isinstance(v, str) else v))
    return '?'.join([url, '&'.join([k.decode() + '=' + quote(v.decode()).replace(' ', '+') for k, v in result])])

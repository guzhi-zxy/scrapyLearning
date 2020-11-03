# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: utils.py
@time: 2020-11-03 12:06:30
@projectExplain: 
"""

from urllib.parse import urlparse

from common_servers.conf import ENV, ENV_PROD

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

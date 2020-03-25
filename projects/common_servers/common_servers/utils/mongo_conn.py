# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: mongo_conn.py
@time: 2020-03-20 12:01:24
@projectExplain: 
"""
from pymongo import MongoClient
from dynaconf import settings


def connect_mongodb():
    mongo_client = MongoClient(settings.MONGO_IPS)
    if settings.MONGO_USER:
        mongo_client.admin.authenticate(settings.MONGO_USER, settings.MONGO_PWD)
    return mongo_client


def connect_mongo(config: dict = settings.mongodb['mongo']):
    '''
    切换自建mongodb集群使用
    :param config:
    :return:
    '''
    mongo_client = MongoClient(config['ips'])
    if config['user']:
        mongo_client.admin.authenticate(config['user'], config['password'])
    return mongo_client

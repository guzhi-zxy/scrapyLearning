# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: mongo_coll_name_update.py
@time: 2020-09-15 18:01:33
@projectExplain: 
"""

import time
import datetime
import threading
from common_servers.conf import connect_low_mongo


class updateCollectionNameBase(object):
    """
    当单表数据量大于100w时，ttl对cpu占用过高，采用按日期对大表切割，定期drop表的策略
    按日期对表名进行更新 - 直接返回链接表面
    此base适合单个表的连接使用
    """
    db = ''
    collection = ''

    def __init__(self):
        self.low_mongo_client = connect_low_mongo()
        self.start_time = 0
        self.sleep_times = 5

    def _update_info(self):
        self.save_coll = self.low_mongo_client[self.db][
            f"{self.collection}_{''.join(str(datetime.date.today()).split('-'))}"]

    def _update_task(self):
        while True:
            if int(time.time()) >= self.start_time:
                self._update_info()
                self.start_time = int(
                    time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=1)), '%Y-%m-%d')))
            time.sleep(self.sleep_times)

    def start_update(self):
        self._update_info()

        t = threading.Thread(target=self._update_task)
        t.daemon = True
        t.start()


class checkCollectionsNameBase(object):
    start_time = 0
    sleep_times = 10

    def __init__(self, collection=None):
        self.collection = collection

    def _update_task(self):
        while True:
            if int(time.time()) >= self.start_time:
                self.check_collections()
                self.flush_collections()
                self.start_time = int(
                    time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=1)), '%Y-%m-%d')))
            time.sleep(self.sleep_times)

    def start_update(self):
        self.check_collections()
        self.flush_collections()
        t = threading.Thread(target=self._update_task)
        t.daemon = True
        t.start()

    def check_collections(self):
        if isinstance(self.collection, list):
            self.save_coll = [f"{coll}_{''.join(str(datetime.date.today()).split('-'))}" for coll in self.collection]
        else:
            self.save_coll = f"{self.collection}_{''.join(str(datetime.date.today()).split('-'))}"

    def flush_collections(self):
        raise NotImplementedError


class connectMongoBase(checkCollectionsNameBase):
    """
    当单表数据量大于100w时，ttl对cpu占用过高，采用按日期对大表切割，定期drop表的策略
    按日期对表名进行更新 - 直接返回链接表面
    此base适合一个db下切割一个或多个表
    支持 str list 两种传入类型
        - str 为单表切割   # 单表时直接返回单表的连接，可直接使用
        - list 为多表切割  # 多表时返回多表的字典，key: value = 表名: 表的连接
    """

    def __init__(self, db=None, collection=None):
        super(connectMongoBase, self).__init__()
        self.low_mongo_client = connect_low_mongo()
        self.db = db
        self.collection = collection

    def flush_collections(self):
        if isinstance(self.collection, list):
            self.colls = [self.low_mongo_client[self.db][coll] for coll in self.save_coll]
            self._coll = dict(zip(self.collection, self.colls))
        else:
            self._coll = self.low_mongo_client[self.db][self.save_coll]

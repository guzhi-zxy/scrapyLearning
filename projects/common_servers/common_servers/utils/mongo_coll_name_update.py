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
from conf import connect_low_mongo


class updateCollectionNameBase(object):
    """
    当单表数据量大于100w时，ttl对cpu占用过高，采用按日期对大表切割，定期drop表的策略
    按日期对表名进行更新
    """
    db = ''
    collection = ''

    def __init__(self):
        self.low_mongo_client = connect_low_mongo()
        self.start_time = 0
        self.sleep_times = 5

    def _update_info(self):
        self.save_coll = self.low_mongo_client[self.db][f"{self.collection}_{''.join(str(datetime.date.today()).split('-'))}"]

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


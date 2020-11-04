# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: save_mongo.py
@time: 2020-01-03 14:15:25
@projectExplain: mongodb 插入、更新、删除
"""

from common_servers.lib.utils import connect_mongo


class SaveMongo(object):
    def __init__(self, db, collection):
        self.db = db
        self.collection = collection
        self.client = connect_mongo()
        self.coll = self.client[self.db][self.collection]

    def _insert(self, data: dict):
        '''
        插入一条数据
        当数据中有非法字符时用此方式插入
        :param data:
        :return:
        '''
        self.coll.insert(data, check_keys=False)

    def _insert_one(self, data: dict):
        '''
        插入一条数据
        :param data:
        :return:
        '''
        self.coll.insert_one(data)

    def _insert_many(self, data_list: list, ordered=True):
        '''
        插入多条数据
        :param data_list:
        :param ordered:
        :return:
        '''
        self.coll.insert_many(data_list, ordered=ordered)

    def _update(self, filter_data: dict, data: dict, upsert=False, multi=False):
        '''
        更新数据
        :param filter_data: 条件
        :param data: 数据
        :param upsert: 默认没有不插入，True没有则插入
        :param multi: 默认更新匹配到的第一条，True 更新匹配到的所有条
        :return:
        '''
        self.coll.update(filter_data, {"$set": data}, upsert, multi)

    def _update_part(self, filter_data: dict, data: dict, invariant_data: dict, upsert=False, multi=False):
        '''
        更新部分数据
        :param filter_data: 条件
        :param data: 数据 (可包含不需要更新的数据)
        :param invariant_data: 不需要更新的数据
        :param upsert: 默认没有不插入，True没有则插入
        :param multi: 默认更新匹配到的第一条，True 更新匹配到的所有条
        :return:
        '''
        for key in invariant_data.keys():
            try:
                del data[key]
            except:
                pass
        self.coll.update(filter_data, {"$set": data, "$setOnInsert": invariant_data}, upsert, multi)

    def _delete_one(self, filter_data: dict):
        '''
        删除一条数据
        :param filter_data:
        :return:
        '''
        self.coll.delete_one(filter_data)

    def _delete_many(self, filter_data: dict):
        '''
        删除多条数据
        :param filter_data:
        :return:
        '''
        self.coll.delete_many(filter_data)

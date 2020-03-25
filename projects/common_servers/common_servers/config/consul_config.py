# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: consul_config.py
@time: 2020-03-20 11:57:54
@projectExplain: 
"""
import consul
import time
import threading
import toml
from typing import List


class ConsulConfig(object):
    def __init__(self, keys: List[str], watch: bool = False, interval: int = 5):
        self.config_dict = {}
        self.interval = interval
        if watch:
            for key in keys:
                self.consul_config_watch(key)
        else:
            for key in keys:
                self.consul_config(key)

    def consul_config_with_watch(self, key: str):
        c = consul.Consul()
        index = None
        try:
            index, data = c.kv.get(key, index=index)
            config = str(data['Value'], encoding='utf-8')
            res = toml.loads(config)
            for k, v in res.items():
                self.config_dict[k.lower()] = v
        except consul.Timeout:
            self.config_dict[key] = None

    def consul_config_watch(self, key: str):
        self.consul_config_with_watch(key)
        t = threading.Thread(target=self.consul_config_worker, args=(key,))
        t.daemon = True
        t.start()

    def consul_config_worker(self, key: str):
        while True:
            time.sleep(self.interval)
            self.consul_config_with_watch(key)

    # 根据key取consul配置，监听配置变化
    # def get_consul_config_with_watch(self, key: str):
    #     return self.config_dict.get(key)

    # 根据key取consul配置，不监听配置变化
    def consul_config(self, key: str):
        c = consul.Consul()
        try:
            index = None
            index, data = c.kv.get(key, index=index)
            config = str(data['Value'], encoding='utf-8')
            res = toml.loads(config)
            for k, v in res.items():
                self.config_dict[k.lower()] = v
        except consul.Timeout:
            return None

    def __getattr__(self, item: str):
        return self.config_dict[item.lower()]

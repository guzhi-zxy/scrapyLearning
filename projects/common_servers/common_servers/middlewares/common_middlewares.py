# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: common_middlewares.py
@time: 2020-10-14 16:47:51
@projectExplain: 
"""

import random
from common_servers.config.user_agents import phone_ua, chrome_ua


class UASetDownloaderMiddleware(object):
    '''
    ua设置中间件 建议优先级设置低点 确保ua不被覆盖
    默认设置Chrome ua
    如需设置phone ua 需带着 need_phone_ua
    meta['need_phone_ua'] = True
    '''

    def process_request(self, request, spider):
        if request.meta.get('need_phone_ua') == True:
            request.headers["User-Agent"] = random.choice(phone_ua)
        else:
            request.headers["User-Agent"] = random.choice(chrome_ua)

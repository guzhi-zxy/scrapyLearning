# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: proxy_middlewares.py
@time: 2020-03-20 11:36:07
@projectExplain: 支持比如一个 spider 存在需要代理和不需要代理的情况，如果不需要按照如下设置
yield scrapy.Request(
    url,
    meta = {
        'dont_proxy': True
        }
    )
"""

import sys
import base64
import random
from lib.log import get_influx_logger
from conf import PROJECT_NAME

logger_influx = get_influx_logger('proxy')


class ProxyAbyMiddleware(object):
    """
    阿布云代理
    """

    # 代理隧道验证信息
    proxyUser = ""
    proxyPass = ""

    proxyServer = "http://http-dyn.abuyun.com:9020"
    proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")

    def process_request(self, request, spider):
        if not request.meta.get('dont_proxy'):
            request.meta['proxy'] = self.proxyServer
            request.headers['Porxy-Authorization'] = self.proxyAuth
            logger_influx.info(f'proxy_req, name={self.proxyUser},project={PROJECT_NAME},spider={spider.name} value=1')

    def process_response(self, request, response, spider):
        if request.meta.get('dont_proxy'):
            request.meta['dont_proxy'] = False  # 默认每个请求都用代理，如果不用，请求时在 meta 中设置
        else:
            logger_influx.info(
                f'proxy_resp,name={self.proxyUser},project={PROJECT_NAME},spider={spider.name},status={response.status} value=1')
            if response.status == 429:
                return request
        return response


PY3 = sys.version_info[0] >= 3


def base64ify(bytes_or_str):
    if PY3 and isinstance(bytes_or_str, str):
        input_bytes = bytes_or_str.encode('utf8')
    else:
        input_bytes = bytes_or_str

    output_bytes = base64.urlsafe_b64encode(input_bytes)
    if PY3:
        return output_bytes.decode('ascii')
    else:
        return output_bytes


class Proxy16Middleware(object):
    '''
    16云
    '''
    proxyHost = "u1421.300.tp.16yun.cn"
    proxyPort = "6475"

    # 代理隧道验证信息
    proxyUser = ""
    proxyPass = ""

    def process_request(self, request, spider):
        if not request.meta.get('dont_proxy'):
            request.meta['proxy'] = "http://{0}:{1}".format(self.proxyHost, self.proxyPort)

            # 添加验证头
            encoded_user_pass = base64ify(self.proxyUser + ":" + self.proxyPass)
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

            # 设置IP切换头(根据需求)
            tunnel = random.randint(1, 10000)
            request.headers['Proxy-Tunnel'] = str(tunnel)
            logger_influx.info(f'proxy_req,name={self.proxyUser},project={PROJECT_NAME},spider={spider.name} value=1')

    def process_response(self, request, response, spider):
        if request.meta.get('dont_proxy'):
            request.meta['dont_proxy'] = False  # 默认每个请求都用代理，如果不用，请求时在 meta 中设置
        else:
            logger_influx.info(
                f'proxy_resp,name={self.proxyUser},project={PROJECT_NAME},spider={spider.name},status={response.status} value=1')
            if response.status == 429:
                return request
        return response

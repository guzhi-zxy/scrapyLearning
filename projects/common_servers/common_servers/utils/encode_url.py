# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: encode_url.py
@time: 2020-04-26 12:09:29
@projectExplain: scrapy.Request url参数一次性完成拼接 参考requests.get中params参数底层拼接方法
"""
from urllib.parse import quote


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

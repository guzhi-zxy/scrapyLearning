# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: zomato.py
@time: 2020-10-16 15:25:37
@projectExplain: https://www.zomato.com/atlanta 有意思的记录
只对 web UA 做了检测限制
对 phone UA 未做限制
"""
import requests
def test1():
    headers = {
        'authority': 'www.zomato.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',

        # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9',
    }

    proxies = {
        "http": 'http://127.0.0.1:6868',
        "https": 'https://127.0.0.1:6868',
    }
    response = requests.get('https://www.zomato.com/atlanta', headers=headers, proxies=proxies)
    print(response.status_code)
    print(response.text)

test1()
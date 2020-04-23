# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: random_ip_mac_ua.py
@time: 2020-04-23 16:01:23
@projectExplain: 
"""

import random
import socket
import struct

from fake_useragent import UserAgent

def get_random(length):
    '''
    生成 16位android 或 32位imei_md5
    :param length:
    :return:
    '''
    # 条件 length <= len(start_data) 超过的话random.sample支持
    start_data = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.sample(start_data, length))


def get_random_ip():
    '''
    生成IP
    :return:
    '''
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


def random_mac():
    '''
    生成mac地址
    :return:
    '''
    mac = [0x52, 0x54, 0x00,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


def get_userAgent():
    '''
    生成user-agent
    :return:
    '''
    return UserAgent(verify_ssl=False).random



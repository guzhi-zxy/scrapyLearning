# -*- coding: utf-8 -*-

import socket
import logging
import os
import json
import requests
from pymongo import MongoClient
from logging import handlers
from dynaconf import settings as conf_settings

try:
    from cloghandler import ConcurrentRotatingFileHandler as RFHandler
except ImportError:
    # Next 2 lines are optional:  issue a warning to the user
    from warnings import warn

    warn("ConcurrentLogHandler package not installed.  Using builtin log handler")
    from logging.handlers import RotatingFileHandler as RFHandler

token_url = 'https://oapi.dingtalk.com/robot/send?access_token=42efbbbee0fca80611ef1ee109e1fe61751068cc349c34bfbdfd5a533ab5d502'


class Inintal(object):
    '''
    初始化spider __init__
    '''

    def __init__(self, *args, **kwargs):
        self._job = kwargs.get("_job", "")
        self._version = kwargs.get("_version", "")


def get_ip_address():
    # 获取本机计算机名称
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        # 下面这两种种方法同样可以
        # fqdnName = socket.getfqdn(socket.gethostname())
        # ip = socket.gethostbyname(fqdnName)
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(('baidu.com', 0))
        # ip = s.getsockname()[0]
    except:
        # 获取IP地址失败
        ip = "127.0.0.1"
    return ip


def get_pid():
    try:
        import os
        return os.getpid()
    except:
        return 0


def get_mgo_client():
    mongo_ips = conf_settings.MONGO_IPS
    mongo_auth_user = conf_settings.MONGO_USER
    mongo_auth_pwd = conf_settings.MONGO_PWD
    mongo_client = MongoClient(
        mongo_ips,
        w=1,
        # readPreference="secondaryPreferred"
    )
    if mongo_auth_user:
        mongo_client.admin.authenticate(mongo_auth_user, mongo_auth_pwd)
    return mongo_client


def get_influx_logger(log_name, backup=3, has_parent=False):
    log_dir = os.path.join(conf_settings.LOG_DIR, 'monitor_stats')
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    os.path.exists(os.path.abspath(log_dir)) or os.mkdir(os.path.abspath(log_dir))
    filename = os.path.join(log_dir, '{}.log'.format(log_name))
    th = RFHandler(filename, encoding="utf-8", maxBytes=100 * 1024 * 1024, backupCount=backup)
    logger.addHandler(th)
    if not has_parent:
        logger.parent = None
    return logger


def dd_notice(content, token_url):
    """
    钉钉机器人
    """
    content = "Spider - {}".format(content)
    data = {
        "msgtype": "text",
        "text": {
            "content": content,
        },
    }
    data = json.dumps(data)
    h = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.post(token_url, headers=h, data=data)
    return r.text


if __name__ == '__main__':
    mongo_ips, mongo_auth_user, mongo_auth_pwd = conf_settings.MONGO_IPS, conf_settings.MONGO_USER, conf_settings.MONGO_PWD
    print(mongo_ips, mongo_auth_user, mongo_auth_pwd)

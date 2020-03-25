# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: log.py
@time: 2020-03-20 11:53:28
@projectExplain: 
"""

import os
import time
import socket
import logging
import datetime
from logging import handlers
from pythonjsonlogger import jsonlogger
from cloghandler import ConcurrentRotatingFileHandler

from conf import LOG_DIR, LOG_LEVEL, ENV, PROJECT_NAME


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self, *args, **kwargs):
        super(CustomJsonFormatter, self).__init__(*args, **kwargs)
        self.hn = socket.gethostname()

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["hn"] = self.hn
        log_record["project"] = PROJECT_NAME
        log_record["log_level"] = record.levelname
        log_record["timestamp_ms"] = int(time.time() * 1000)
        log_record["datetime"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+08:00"


def get_influx_logger(logger_name, log_size=100 * 1024 * 1024, backupCount=2):
    '''

    :param logger_name:
    :param log_size:
    :param backupCount:
    :return:
    '''
    logger_name = "influx_{}".format(logger_name.lower())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    log_name = os.path.join(LOG_DIR, "{}.log".format(logger_name))

    rotate_handler = ConcurrentRotatingFileHandler(log_name, mode="a", maxBytes=log_size, backupCount=backupCount)
    rotate_handler.setLevel(logging.INFO)
    logger.addHandler(rotate_handler)

    return logger


def get_logger(log_name: str, when='D', backupCount=3):
    formatter = logging.Formatter("[%(asctime)s %(filename)s %(funcName)s line:%(lineno)d %(levelname)s]: %(message)s")

    logger = logging.getLogger(log_name)
    logger.setLevel(LOG_LEVEL)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    filename = os.path.join(LOG_DIR, f'{log_name}.log')
    th = handlers.TimedRotatingFileHandler(
        filename=filename,
        when=when,
        backupCount=backupCount,
        encoding='utf-8'
    )
    th.setFormatter(formatter)
    logger.addHandler(th)

    return logger


def get_json_logger(logger_name, log_size=512 * 1024 * 1024, backupCount=2):
    '''

    :param logger_name:
    :param log_size: default 512M
    :param backupCount:
    :return:
    '''
    formatter = CustomJsonFormatter("%(filename)s %(lineno)d %(funcName)s %(message)s")

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    log_name = os.path.join(LOG_PATH, "{}.log".format(logger_name))

    # rotate_handler = handlers.TimedRotatingFileHandler(
    #     filename=log_name,
    #     when=when,
    #     backupCount=backupCount,
    #     encoding='utf-8'
    # )
    rotate_handler = ConcurrentRotatingFileHandler(log_name, mode="a", maxBytes=log_size,
                                                   backupCount=backupCount)  # 每个文件最多保存512M
    rotate_handler.setLevel(logging.INFO)
    rotate_handler.setFormatter(formatter)

    logger.addHandler(rotate_handler)
    return logger

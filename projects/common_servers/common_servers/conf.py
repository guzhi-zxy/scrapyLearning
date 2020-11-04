# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: conf.py
@time: 2020-03-20 11:51:18
@projectExplain: 配置
"""
import os

from dynaconf import settings as dynaconf_settings

from common_servers.config.consul_config import ConsulConfig

PROJECT_NAME = ''

ENV_LOCAL = 'local'
ENV_DEV = 'development'
ENV_PROD = 'production'

ENV = dynaconf_settings.current_env

if ENV == ENV_LOCAL:
    consul_keys = [f'config/spider/{PROJECT_NAME},local/data']
elif ENV == ENV_DEV:
    consul_keys = [f'config/spider/{PROJECT_NAME},dev/data']
else:
    consul_keys = [f'config/spider/{PROJECT_NAME},prod/data']

consul_settings = ConsulConfig(consul_keys, watch=True)

LOG_DIR = os.path.join(consul_settings.LOG_DIR, PROJECT_NAME)
LOG_LEVEL = consul_settings.LOG_LEVEL

MYSQL_READ_PRODUCT = consul_settings.mysql['product']

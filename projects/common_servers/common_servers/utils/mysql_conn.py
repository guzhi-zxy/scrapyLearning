# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: mysql_conn.py
@time: 2020-03-20 12:04:28
@projectExplain: 
"""

import pymysql
from dynaconf import settings

DRDS_DB_PROD = settings.drds


def get_mysql_connection(db):
    db_conf = DRDS_DB_PROD.copy()
    db_conf['db'] = db
    connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, autocommit=True, **db_conf)
    return connection

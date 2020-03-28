# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: trace_middlewares.py
@time: 2020-03-25 23:48:06
@projectExplain: 
"""

'''
trace_id跟踪

目的: 生成新的trace_id, 如果有trace_id直接使用


Fluent相关

注意:
- 日志文件所在目录用户必须是td-agnet, 否则会提示无权限

# 安装
curl -L https://toolbelt.treasuredata.com/sh/install-redhat-td-agent3.sh | sh 
 
# 安装mongo插件
td-agent-gem install fluent-plugin-mongo
 
 
# 服务器配置地址: /etc/td-agent/config.d
 
 
# td-agent日志(可以排查错误): /var/log/td-agent/td-agent.log
 
 
# 常用命令
/etc/init.d/td-agent restart
/etc/init.d/td-agent stop

'''

import uuid
from lib.log import get_json_logger

log_instances = {}


def log(spider_name: str):
    spider_name = "fluent_{}".format(spider_name)
    if not log_instances.get(spider_name):
        log_instances[spider_name] = get_json_logger(spider_name)
    return log_instances[spider_name]


class TraceMiddleware(object):
    def process_request(self, request, spider):
        # 如果没有trace_id直接生成一个
        if not request.meta.get('trace_id'):
            request.meta['trace_id'] = str(uuid.uuid4())
        request.meta['spider_name'] = spider.name
        request.meta['req_url'] = request.url

        log(spider.name).info('', extra=request.meta)

    def process_response(self, request, response, spider):
        if request.meta.get('trace_id'):
            # extra不直接使用meta, 因为meta可能会很大
            log(spider.name).info('', extra={
                'trace_id': request.meta['trace_id'],
                'spider_name': spider.name,
                'download_latency': request.meta['download_latency'],
                'req_url': request.url,
                'res_url': response.url,
            })
        return response
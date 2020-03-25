# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: retry_middlewares.py
@time: 2020-03-20 14:14:13
@projectExplain: scrapy自带重试中间件RetryMiddleware默认已经启用, 以下仅仅是在原有基础上多记录了一行log, 并没有做其它操作
"""

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from lib.log import get_logger

logger = get_logger('midd_retry')


class TimeoutMiddleware(RetryMiddleware):
    '''
    超时重试

    RetryMiddleware内部已经做了比较好的超时重试策略, 此处仅仅是记录了重试失败后的log
    '''

    def process_exception(self, request, exception, spider):
        retry_times = request.meta.get('retry_times', 0)
        logger.info(
            f'spider: {spider.name} timeout_exception, retry_times:{retry_times} over max_retry_times:{self.max_retry_times}. ignore url:{request.url}')
        return super(TimeoutMiddleware, self).process_exception(request, exception, spider)


class MaxRetryAccessMiddleware(RetryMiddleware):
    '''
    重试超过最大次数后，返回配置化数据，而不是最终抛出异常丢掉请求
    该类继承自 RetryMiddleware，也就是源码的 类继承
    需关闭 默认重试中间件 开启自定义中间件
    中间件orderCode不能过大，不能先走自定义的中间件，不然无法默认重试
    '''

    def __init__(self, settings):
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        retries = request.meta.get('retry_times', 0) + 1
        if retries > self.max_retry_times:
            # 超过重试次数，直接往下走
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 如果返回了[500, 502, 503, 504, 522, 524, 408]这些code，do something
            pass
            return self._retry(request, reason, spider) or response

        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

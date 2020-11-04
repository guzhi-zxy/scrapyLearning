# -*- coding:utf-8 -*-

'''
爬虫运行情况
'''

from twisted.internet import task
from scrapy import signals
from scrapy.exceptions import NotConfigured
from common_servers.extensions.utils import get_influx_logger

logger_influx = get_influx_logger('extension_sch_nums')


class SchNums(object):
    interval = 1

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.crawler = crawler
        if not self.interval:
            raise NotConfigured
        sg = crawler.signals
        sg.connect(self._spider_opened, signal=signals.spider_opened)
        sg.connect(self._spider_closed, signal=signals.spider_closed)
        sg.connect(self._request_scheduled, signal=signals.request_scheduled)
        sg.connect(self._item_scraped, signal=signals.item_scraped)
        sg.connect(self._spider_errored, signal=signals.spider_error)
        sg.connect(self._item_errored, signal=signals.item_error)

        self.sch_nums = 0
        self.item_nums = 0
        self.spider_error_nums = 0
        self.item_error_nums = 0

    def _spider_opened(self, spider):
        self.task = task.LoopingCall(self._log, spider)
        self.task.start(self.interval)

    def _spider_closed(self, spider, reason):
        if self.task.running:
            self.task.stop()

    def _request_scheduled(self, request, spider):
        self.sch_nums += 1

    def _item_scraped(self, item, response, spider):
        self.item_nums += 1

    def _spider_errored(self, failure, response, spider):
        self.spider_error_nums += 1

    def _item_errored(self, item, response, spider, failure):
        self.item_error_nums += 1

    def _log(self, spider):
        logger_influx.info('scrapy_cnt,project={},spider={} sch_nums={},item_nums={},spider_error_nums={},item_error_nums={}'.format('superHotItemPool', spider.name, self.sch_nums, self.item_nums,
                                                                                                                                     self.spider_error_nums, self.item_error_nums))
        self.sch_nums = 0
        self.item_nums = 0
        self.spider_error_nums = 0
        self.item_error_nums = 0

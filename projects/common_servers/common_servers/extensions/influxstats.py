"""
通用监控插件
用于输出Influx日志
监控爬虫运行情况
"""
import logging
import os

from twisted.internet import task
from scrapy import signals

from common_servers.extensions.utils import get_ip_address, get_pid, get_influx_logger


class MonitorStats(object):
    """Log basic scraping stats periodically"""

    def __init__(self, stats, bot_name="bot_name", interval=60.0):
        self.prev_stats = stats.get_stats().copy()
        self.stats = stats
        self.interval = interval
        self.task = None
        self.ip = get_ip_address()
        self.pid = get_pid()
        self.logger = get_influx_logger("influx_monitor_stats_{}".format(bot_name))
        self.project = None

        self.item_error_nums = 0
        self.spider_error_nums = 0
        self.item_dropped_nums = 0
        self.request_dropped_nums = 0
        self.request_scheduled_nums = 0

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('INFLUXSTATS_INTERVAL', 10)
        bot_name = crawler.settings.get('BOT_NAME', "project_name")
        o = cls(crawler.stats, bot_name, interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)

        crawler.signals.connect(o._item_errored, signal=signals.item_error)
        crawler.signals.connect(o._spider_errored, signal=signals.spider_error)
        crawler.signals.connect(o._request_dropped, signal=signals.request_dropped)
        crawler.signals.connect(o._item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(o._request_scheduled, signal=signals.request_scheduled)

        return o

    def _item_errored(self, item, response, spider, failure):
        self.item_error_nums += 1

    def _spider_errored(self, failure, response, spider):
        self.spider_error_nums += 1

    def _item_dropped(self, item, exception, spider):
        self.item_dropped_nums += 1

    def _request_dropped(self, request, spider):
        self.request_dropped_nums += 1

    def _request_scheduled(self, request, spider):
        self.request_scheduled_nums += 1

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.monitor, spider)
        self.task.start(self.interval)

    def monitor(self, spider):
        """
        :param spider:
        :return:
        """
        if self.project is None:
            self.project = spider.settings["BOT_NAME"]
        stats = self.stats.get_stats()
        delta_labels = {}
        for k in stats:
            now = stats[k]
            if isinstance(now, int):
                prev = self.prev_stats.get(k, 0)
                delta_labels[k] = now - prev
        self.prev_stats = stats.copy()

        pages, items = delta_labels.get("response_received_count", 0), delta_labels.get("item_scraped_count", 0)

        # 抓取页数,item,抛出异常统计
        self.logger.debug(
            f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid}"
            f" pages={pages},items={items},spider_error={self.spider_error_nums},item_error={self.item_error_nums},"
            f"item_dropped={self.item_dropped_nums},sch_nums={self.request_scheduled_nums},"
            f"req_nums={delta_labels.get('downloader/request_count', 0)},"
            f"resp_nums={delta_labels.get('downloader/response_count', 0)},req_drop={self.request_dropped_nums}")

        self.item_error_nums = 0
        self.spider_error_nums = 0
        self.item_dropped_nums = 0
        self.request_dropped_nums = 0
        self.request_scheduled_nums = 0

        # 重试次数和原因的监控
        retry_stats = {}
        # 日志统计
        log_stats = {}
        for k in delta_labels:
            if k.startswith("retry/reason_count"):
                reason = k.split("/")[-1].split(".")[-1]
                retry_stats[reason] = delta_labels[k]
            elif k.startswith("log_count"):
                log_stats[k.split("/")[-1]] = delta_labels[k]

        if len(log_stats):
            self.logger.debug(
                f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                f"plugin=log_count debug={log_stats.get('DEBUG', 0)},info={log_stats.get('INFO', 0)},"
                f"error={log_stats.get('ERROR', 0)}")

        if len(retry_stats):
            retry_stats["retry_total"] = delta_labels.get("retry/count", 0)
            retry_stats["retry_max_reached"] = delta_labels.get("retry/max_reached", 0)
            for name in retry_stats:
                if retry_stats[name] == 0:
                    continue
                self.logger.debug(
                    f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                    f"plugin=retry,label={name} value={retry_stats[name]}")

        if "scheduler/dequeued/redis" in delta_labels:
            self.logger.debug(
                f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                f"plugin=screpy_redis dequeued={delta_labels['scheduler/dequeued/redis']},"
                f"enqueued={delta_labels.get('scheduler/enqueued/redis', 0)}")

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()

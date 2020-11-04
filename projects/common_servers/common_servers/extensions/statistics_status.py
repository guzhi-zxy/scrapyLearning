# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: statistics_status.py
@time: 2020-01-16 11:09:04
@projectExplain:
"""

import time
import datetime

from twisted.internet import task
from scrapy import signals
from scrapy.exceptions import NotConfigured
from common_servers.extensions.utils import get_influx_logger, get_ip_address, get_pid, dd_notice, token_url


class Statistics(object):
    """Log basic scraping stats periodically"""

    db = 'scrapyd'
    collection = 'spiders'

    def __init__(self, crawler, bot_name="bot_name", *args, interval=60.0, **kwargs):
        self.crawler = crawler
        self.prev_stats = crawler.stats.get_stats().copy()
        self.stats = crawler.stats
        self.interval = interval
        self.task = None
        self.ip = get_ip_address()
        self.pid = get_pid()
        self.stats_logger = get_influx_logger("influx_monitor_stats_{}".format(bot_name))
        self.project = None

        self.item_error_nums = 0
        self.spider_error_nums = 0
        self.item_dropped_nums = 0
        self.request_dropped_nums = 0
        self.request_scheduled_nums = 0
        # self.mongo = SaveMongo(db=self.db, collection=self.collection)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        interval = crawler.settings.getfloat('INFLUXSTATS_INTERVAL', 10)
        bot_name = crawler.settings.get('BOT_NAME', "project_name")
        o = cls(crawler, bot_name, interval, *args, **kwargs)
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
        '''
        spider 状态存储 钉钉报警
        :param spider:
        :return:
        '''
        create_time = datetime.datetime.now()
        # insert_data = {
        #     'pid': get_pid(),
        #     'spider_name': spider.name,
        #     'jobid': spider._job,
        #     'create_time': create_time,
        #     'update_time': create_time,
        #     'status': 'running',
        #     'server': get_ip_address(),
        # }
        # self.mongo._insert_one(insert_data)

        self.task = task.LoopingCall(self.monitor, spider)
        self.task.start(self.interval)
        self.monitor_engine_task = task.LoopingCall(self.monitor_engine_status, spider)
        self.monitor_engine_task.start(1)

        dd_notice(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, spidername: {spider.name}, jobid: {spider._job} 任务启动...",
            token_url)

    def monitor_engine_status(self, spider):
        engine = self.crawler.engine
        """
        f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
        f"plugin=engine run_time={time.time()-engine.start_time},"                      # engine 运行时间
        f"engine_downloader_active={len(engine.downloader.active)},"                    # 下载器中正在下载的数量
        f"engine_scraper_is_idle={1 if engine.scraper.is_idle() else 0},"               # engine是否空闲
        f"engine_spider_is_idle={1 if engine.spider_is_idle(engine.spider) else 0},"    # spider是否空闲
        f"engine_slot_inprogress={len(engine.slot.inprogress)},"                        # 正在处理中的Request数量, 从调度器到下载器的数量
        f"engine_slot_scheduler_dqs={len(engine.slot.scheduler.dqs or [])},"            # 持久度的磁盘调度器队列大小，需要提前指定
        f"engine_slot_scheduler_mqs={len(engine.slot.scheduler.mqs)},"                  # 内存调度器队列大小，默认 调度队列类型
        f"engine_scraper_slot_queue={len(engine.scraper.slot.queue)},"                  # queue() 正在处理的响应队列大小，先进先出，先降下载器下载完成的请求响应加入到slot.queue，然后将需要spider处理的响应加入slot.active，待处理完从slot.active移出
        f"engine_scraper_slot_active={len(engine.scraper.slot.active)},"                # set({}) 在Spider中处理的响应数
        f"engine_scraper_slot_active_size={engine.scraper.slot.active_size},"           # 在Spider中处理的响应的总大小 (bytes)
        f"engine_scraper_slot_itemproc_size={engine.scraper.slot.itemproc_size},"       # 在Pipeline处理中的item数, 处理中 +1, 处理完 -1
        f"engine_scraper_slot_needs_backout={1 if engine.scraper.slot.needs_backout() else 0}"      # 是否需要退出，当前 self.active_size > self.max_active_size时，max_active_size = 5000000,
                                                                                                # 当Pipeline吞吐量远低于下载器的吞吐量时
        """
        try:
            self.stats_logger.info(
                f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                f"plugin=engine run_time={time.time() - engine.start_time},"
                f"engine_downloader_active={len(engine.downloader.active)},"
                f"engine_scraper_isIdle={1 if engine.scraper.is_idle() else 0},"
                f"engine_spider_isIdle={1 if engine.spider_is_idle(engine.spider) else 0},"
                f"engine_slot_inprogress={len(engine.slot.inprogress)},"
                f"engine_slot_scheduler_dqs={len(engine.slot.scheduler.dqs or [])},"
                f"engine_slot_scheduler_mqs={len(engine.slot.scheduler.mqs)},"
                f"engine_scraper_slot_queue={len(engine.scraper.slot.queue)},"
                f"engine_scraper_slot_active={len(engine.scraper.slot.active)},"
                f"engine_scraper_slot_active_size={engine.scraper.slot.active_size},"
                f"engine_scraper_slot_itemproc_size={engine.scraper.slot.itemproc_size},"
                f"engine_scraper_slot_needsBackout={1 if engine.scraper.slot.needs_backout() else 0}"
            )
        except Exception as e:
            spider.logger.exception("engine init do not finish at the first time.")

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
        self.stats_logger.info(
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
                reason = k.split("/")[-1].split(".")[-1].split(" ")[0]
                retry_stats[reason] = delta_labels[k]
            elif k.startswith("log_count"):
                log_stats[k.split("/")[-1]] = delta_labels[k]

        if len(log_stats):
            self.stats_logger.info(
                f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                f"plugin=log_count debug={log_stats.get('DEBUG', 0)},info={log_stats.get('INFO', 0)},"
                f"error={log_stats.get('ERROR', 0)}")

        if len(retry_stats):
            retry_stats["retry_total"] = delta_labels.get("retry/count", 0)
            retry_stats["retry_max_reached"] = delta_labels.get("retry/max_reached", 0)
            for name in retry_stats:
                if retry_stats[name] == 0:
                    continue
                self.stats_logger.info(
                    f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                    f"plugin=retry,label={name} value={retry_stats[name]}")

        if "scheduler/dequeued/redis" in delta_labels:
            self.stats_logger.info(
                f"spider_monitor_stats,project={self.project},spider_name={spider.name},ip={self.ip},pid={self.pid},"
                f"plugin=screpy_redis dequeued={delta_labels['scheduler/dequeued/redis']},"
                f"enqueued={delta_labels.get('scheduler/enqueued/redis', 0)}")

    def spider_closed(self, spider, reason):
        '''
        当某个spider被关闭时，该信号被发送。该信号可以用来释放每个spider在 spider_opened 时占用的资源。
        :param spider:
        :param reason:
        :return:
        '''
        try:
            update_data = {
                'update_time': datetime.datetime.now(),
                'status': 'finished',
                'reason': reason,
            }
            filter_data = {
                'jobid': spider._job
            }
            # self.mongo._update(filter_data, update_data)

            if self.task and self.task.running:
                self.task.stop()

            if self.monitor_engine_task and self.monitor_engine_task.running:
                self.monitor_engine_task.stop()

            dd_notice(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, spidername: {spider.name}, jobid: {filter_data['jobid']}, reason: {update_data['reason']} 任务关闭...",
                token_url)
        except Exception as e:
            spider.logger.exception("spider close error.")

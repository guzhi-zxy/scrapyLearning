# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy_redis.spiders import RedisSpider
from scrapy_redis import defaults
from common_servers.extensions.utils import Inintal


# class BaseRedisSpider(RedisSpider):
class BaseRedisSpider(Inintal, RedisSpider):
    def setup_redis(self, crawler=None):
        super(BaseRedisSpider, self).setup_redis(crawler)
        # self.pipe = self.server.pipeline()

    def lpop_multi(self, redis_key, batch_size):
        """
        批量拿任务
        redis pipeline 不具备原子性，此处执行有可能会因为抢占导致拿取任务为空影响爬虫性能
        改为lua脚本执行
            1）保证任务执行原子性
            2）提高爬虫性能
        """
        # self.pipe.lrange(redis_key, 0, batch_size - 1)
        # self.pipe.ltrim(redis_key, batch_size, -1)
        # datas, _ = self.pipe.execute()
        redis_lua_script = """
                local spider_key = KEYS[1]
                local batch_size = KEYS[2]
                local get_items = redis.call('LRANGE', spider_key, 0, batch_size-1)
                redis.call('LTRIM', spider_key, batch_size, -1)
                return get_items
            """
        datas = self.server.eval(redis_lua_script, 2, redis_key, batch_size)
        return datas

    def next_requests(self):
        """Returns a request to be scheduled or none."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_data = self.server.spop if use_set else self.lpop_multi
        # XXX: Do we need to use a timeout here?
        found = 0

        datas = fetch_data(self.redis_key, self.redis_batch_size)
        # for data in datas:
        req = self.make_request_from_data(datas)
        if req:
            yield req
            found += datas.__len__()
        else:
            self.logger.debug("Request not made from data: %r", datas)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)


class BaseRedisSpider2(Inintal, RedisSpider):

    def init_spider_log(self, crawler):
        log_file = crawler.settings.get('LOG_FILE')
        if not log_file:
            self.logger.info(f'{self.name} cant find LOG_FILE in settings !')
            return

        import logging
        from cloghandler import ConcurrentRotatingFileHandler

        from scrapy.utils.log import configure_logging

        # Disable default Scrapy log settings.
        configure_logging(install_root_handler=False)

        # Define your logging settings.
        log_format = "[%(asctime)s %(filename)s %(funcName)s line:%(lineno)d %(levelname)s]: %(message)s"

        logging.basicConfig(format=log_format)

        rotate_handler = ConcurrentRotatingFileHandler(log_file, mode="a", maxBytes=1 * 1024 * 1024 * 1024,
                                                       backupCount=2)
        rotate_handler.setFormatter(logging.Formatter(log_format))
        rotate_handler.setLevel(crawler.settings.get('LOG_LEVEL'))

        root_logger = logging.getLogger()
        root_logger.addHandler(rotate_handler)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj = super(BaseRedisSpider2, cls).from_crawler(crawler, *args, **kwargs)
        # init logger
        obj.init_spider_log(crawler)
        return obj

    def setup_redis(self, crawler=None):
        super(BaseRedisSpider2, self).setup_redis(crawler)
        # self.pipe = self.server.pipeline()

    def lpop_multi(self, redis_key, batch_size):
        """
        批量拿任务
        redis pipeline 不具备原子性，此处执行有可能会因为抢占导致拿取任务为空影响爬虫性能
        改为lua脚本执行
            1）保证任务执行原子性
            2）提高爬虫性能
        """
        # self.pipe.lrange(redis_key, 0, batch_size - 1)
        # self.pipe.ltrim(redis_key, batch_size, -1)
        # datas, _ = self.pipe.execute()
        redis_lua_script = """
                        local spider_key = KEYS[1]
                        local batch_size = KEYS[2]
                        local get_items = redis.call('LRANGE', spider_key, 0, batch_size-1)
                        redis.call('LTRIM', spider_key, batch_size, -1)
                        return get_items
                    """
        datas = self.server.eval(redis_lua_script, 2, redis_key, batch_size)
        return datas

    def next_requests(self):
        """Returns a request to be scheduled or none."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_data = self.server.spop if use_set else self.lpop_multi
        # XXX: Do we need to use a timeout here?
        found = 0

        datas = fetch_data(self.redis_key, self.redis_batch_size)
        for data in datas:
            req = self.make_request_from_data(data)
            if req:
                yield req
                found += 1
            else:
                self.logger.debug("Request not made from data: %r", data)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

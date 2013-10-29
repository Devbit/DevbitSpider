import telnetlib
from scrapy import log
import time
from agents import AGENTS
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
import TorCtl

import random

"""
Custom proxy provider. 
"""
class CustomHttpProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://localhost:8123"
    
    
"""
change request header nealy every time
"""
class CustomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent
        #log.msg('User-Agent: ' + agent)


class TimedProxyChange(object):
    conn = None
    last = 0

    def __init__(self, settings):
        self.timelimit = settings.get('TOR_CHANGE_LIMIT')
        if TimedProxyChange.conn is None:
            TimedProxyChange.conn = TorCtl.connect(controlAddr=settings.get('TOR_HOST'),
                                                   controlPort=settings.get('TOR_PORT'),
                                                   passphrase=settings.get('TOR_PASSW'))
            TimedProxyChange.last = 0
            log.msg("Opened!")
        log.msg("Init!")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if TimedProxyChange.conn and time.time() - TimedProxyChange.last > self.timelimit:
            TorCtl.Connection.send_signal(TimedProxyChange.conn, "NEWNYM")
            TimedProxyChange.last = time.time()
            log.msg("Proxy changed!")


class RetryChangeProxyMiddleware(RetryMiddleware):
    conn = None
    last = 0
    timelimit = 0

    def _retry(self, request, reason, spider):
        settings = spider.settings

        if RetryChangeProxyMiddleware.conn is None:
            RetryChangeProxyMiddleware.conn = TorCtl.connect(controlAddr=settings.get('TOR_HOST'),
                                                             controlPort=settings.get('TOR_PORT'),
                                                             passphrase=settings.get('TOR_PASSW'))
            RetryChangeProxyMiddleware.last = 0
            RetryChangeProxyMiddleware.timelimit = settings.get('TOR_CHANGE_LIMIT')

        if isinstance(reason, basestring):
            log.msg('Valid retry, reason: ' + reason + ' for URL ' + request.url, log.INFO)
            if RetryChangeProxyMiddleware.conn and time.time() - RetryChangeProxyMiddleware.last > self.timelimit:
                TorCtl.Connection.send_signal(RetryChangeProxyMiddleware.conn, "NEWNYM")
                RetryChangeProxyMiddleware.last = time.time()
                log.msg('Proxy changed!', log.INFO)
            else:
                log.msg('Proxy not changed!', log.INFO)
            return RetryMiddleware._retry(self, request, reason, spider)
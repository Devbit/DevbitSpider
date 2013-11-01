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
    timelimit = 15

    def process_request(self, request, spider):
        settings = spider.settings

        if TimedProxyChange.conn is None:
            TimedProxyChange.conn = TorCtl.connect(controlAddr=settings.get('TOR_HOST'),
                                                   controlPort=settings.get('TOR_PORT'),
                                                   passphrase=settings.get('TOR_PASSW'))
            TimedProxyChange.last = 0
            TimedProxyChange.timelimit = settings.get('TOR_CHANGE_LIMIT')

        t = time.time()
        diff = t - TimedProxyChange.last
        if TimedProxyChange.conn and diff > TimedProxyChange.timelimit:
            TorCtl.Connection.send_signal(TimedProxyChange.conn, "NEWNYM")
            TimedProxyChange.last = t
            log.msg('Proxy changed! New last: %s' % time.strftime("%H:%M:%S"), log.INFO)
        else:
            log.msg('Proxy not changed! Time difference is %s seconds' % ("{:.2f}".format(diff)), log.INFO)


class RetryChangeProxyMiddleware(RetryMiddleware):
    conn = None
    last = 0
    timelimit = 15

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
            t = time.time()
            diff = t - RetryChangeProxyMiddleware.last
            if RetryChangeProxyMiddleware.conn and diff > RetryChangeProxyMiddleware.timelimit:
                TorCtl.Connection.send_signal(RetryChangeProxyMiddleware.conn, "NEWNYM")
                RetryChangeProxyMiddleware.last = t
                log.msg('Proxy changed! New last: %s' % time.strftime("%H:%M:%S"), log.INFO)
            else:
                log.msg('Proxy not changed! Time difference is %s seconds' % ("{:.2f}".format(diff)), log.INFO)
            return RetryMiddleware._retry(self, request, reason, spider)
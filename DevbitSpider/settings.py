# Scrapy settings for CrawlerTest project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from scrapy import log

BOT_NAME = 'DevbitSpider'

SPIDER_MODULES = ['DevbitSpider.spiders']
NEWSPIDER_MODULE = 'DevbitSpider.spiders'

DOWNLOADER_MIDDLEWARES = {
    #'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
    #'DevbitSpider.middleware.RandomProxy': 100,
    #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'DevbitSpider.middleware.CustomHttpProxyMiddleware': 543,
    'DevbitSpider.middleware.CustomUserAgentMiddleware': 545,
    'DevbitSpider.middleware.RetryChangeProxyMiddleware': 600,
    #'DevbitSpider.middleware.TimedProxyChange': 548,
}

TOR_HOST = 'localhost'
TOR_PORT = 9151
TOR_PASSW = ''
TOR_CHANGE_LIMIT = 10

########### Item pipeline
ITEM_PIPELINES = [
    #"DevbitSpider.pipelines.MySQLStorePipeline",
    #"DevbitSpider.pipelines.MongoDBPipeline",
]

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 8091
MONGODB_DB = 'linkedin_crawl'
MONGODB_COLLECTION = 'profiles'
MONGODB_UNIQ_KEY = '_id'
###########

DOWNLOAD_FILE_FOLDER = 'H:\Development\Python\CrawlerTest\Download';

#AUTOTHROTTLE_ENABLED = True

COOKIES_ENABLED = False

#RETRY_TIMES = 10

RETRY_HTTP_CODES = [999, 500, 503, 504, 400, 403, 408]

#LOG_FILE = 'log.txt'
LOG_LEVEL = log.INFO

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'DevbitSpider (+http://www.yourdomain.com)'

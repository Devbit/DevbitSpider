# Scrapy settings for CrawlerTest project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from scrapy import log

BOT_NAME = 'LinkedinSpider'

SPIDER_MODULES = ['LinkedinSpider.spiders']
NEWSPIDER_MODULE = 'LinkedinSpider.spiders'

DOWNLOADER_MIDDLEWARES = {
    #'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
    #'LinkedinSpider.middleware.RandomProxy': 100,
    #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'LinkedinSpider.middleware.CustomHttpProxyMiddleware': 543,
    'LinkedinSpider.middleware.CustomUserAgentMiddleware': 545,
    'LinkedinSpider.middleware.RetryChangeProxyMiddleware': 600,
    #'LinkedinSpider.middleware.TimedProxyChange': 548,
}

TOR_HOST = 'localhost'
TOR_PORT = 9151
TOR_PASSW = ''
TOR_CHANGE_LIMIT = 30

########### Item pipeline
ITEM_PIPELINES = [
    #"LinkedinSpider.pipelines.MySQLStorePipeline",
    #"LinkedinSpider.pipelines.MongoDBPipeline",
]

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 8091
MONGODB_DB = 'linkedin_crawl'
MONGODB_COLLECTION = 'profiles'
MONGODB_UNIQ_KEY = '_id'

SQL_HOST = "localhost"
SQL_PORT = 3306
SQL_DB = "linkedin_crawl"
SQL_USER = "user"
SQL_PASSWORD = "password"
###########

DOWNLOAD_FILE_FOLDER = 'H:\Development\Python\CrawlerTest\Download';

#AUTOTHROTTLE_ENABLED = True

COOKIES_ENABLED = False

#RETRY_TIMES = 10

RETRY_HTTP_CODES = [999, 500, 503, 504, 400, 403, 404, 408]

#LOG_FILE = 'log.txt'
#LOG_LEVEL = log.INFO

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'LinkedinSpider (+http://www.yourdomain.com)'

import urllib
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy import log
from w3lib.url import url_query_cleaner
from bs4 import UnicodeDammit
from os import path
from DevbitSpider.parsers.ITBanenParser import ITBanenParser
import os

from DevbitSpider.items import CrawlertestItem, PersonProfileItem


class ITBanenSpider(CrawlSpider):
    name = "itbanen"
    allowed_domains = ["itbanen.nl"]
    start_urls = [ "http://www.itbanen.nl/vacature/bladeren/plaatsnaam/%s" % s
                   for s in "abcdefghijklmnopqrstuvwxyz" ]
    #start_urls = [ "http://www.itbanen.nl/vacature/bladeren/plaatsnaam/w" ]

    rules = (
        #Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse(self, response):
        self.state['items_count'] = self.state.get('items_count', 0) + 1
        response = response.replace(url=url_query_cleaner(response.url))
        hxs = HtmlXPathSelector(response)
        index_level = self.determine_level(response)
        if index_level in [1, 2]:
            relative_urls = self.get_follow_links(index_level, hxs)
            if relative_urls is not None:
                for url in relative_urls:
                    yield Request(url, callback=self.parse)
        elif index_level == 3:
            vacature = ITBanenParser.parse_profile(hxs)
            if vacature is None:
                return
            vacature['url'] = UnicodeDammit(response.url).markup
            yield vacature


    def determine_level(self, response):
        """
        determine the index level of current response, so we can decide wether to continue crawl or not.
        level 1: people/[a-z].html
        level 2: people/[A-Z][\d+].html
        level 3: people/[a-zA-Z0-9-]+.html
        level 4: search page, pub/dir/.+
        level 5: profile page
        """
        import re
        url = response.url
        if re.match(".+/plaatsnaam/.+", url):
            return 1
        elif re.match(".+/bladeren/[a-zA-Z]+/\d", url):
            return 2
        elif re.match(".+/vacature/\d+/.+", url):
            return 3
        return None

    def get_follow_links(self, level, hxs):
        if level == 1:
            relative_urls = hxs.select("//div[contains(@class,'three-column')]/ul/li/a/@href").extract()
            return relative_urls
        elif level == 2:
            relative_urls = hxs.select("//ul[@id='vacature-search-results']/li//div[@class='result-item-header']/h2/a/@href").extract()
            return relative_urls
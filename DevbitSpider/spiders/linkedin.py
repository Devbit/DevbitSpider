import urllib
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from w3lib.url import url_query_cleaner
from bs4 import UnicodeDammit
from os import path
from DevbitSpider.parsers.LinkedinProfileParser import LinkedinProfileParser
import os
from bson import ObjectId

from DevbitSpider.items import CrawlertestItem, PersonProfileItem


class LinkedinSpider(CrawlSpider):
    name = "linkedin"
    allowed_domains = ["linkedin.com"]

    def __init__(self, letters="abcdefghijklmnopqrstuvwxyz"):
        self.start_urls = ["http://nl.linkedin.com/directory/people-%s" % s
                           for s in letters]

    rules = (
        #Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse(self, response):
        self.state['items_count'] = self.state.get('items_count', 0) + 1
        response = response.replace(url=url_query_cleaner(response.url))
        #self.log('Page: %s' % response.url)
        hxs = HtmlXPathSelector(response)
        index_level = self.determine_level(response)
        if index_level in [1, 2, 3, 4]:
            #self.save_to_file_system(index_level, response)
            relative_urls = self.get_follow_links(index_level, hxs)
            if relative_urls is not None:
                for url in relative_urls:
                    yield Request(url, callback=self.parse)
        elif index_level == 5:
            #self.log('Level 5, parsing profile');
            linkedin_id = self.get_linkedin_id(response.url)
            person_profile = LinkedinProfileParser.parse_profile(hxs)
            if person_profile is None:
                return
            linkedin_id = UnicodeDammit(urllib.unquote_plus(linkedin_id)).markup
            #self.log('ID: ' + linkedin_id)
            if linkedin_id:
                person_profile['_id'] = linkedin_id
                person_profile['url'] = UnicodeDammit(response.url).markup
                yield person_profile



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
        if re.match(".+-[a-z]$", url):
            return 1
        elif re.match(".+-[a-z]-\d+$", url):
            return 2
        elif re.match(".+-[a-z]-\d+-\d+$", url):
            return 3
        elif re.match(".+/pub/dir/.+", url):
            return 4
        elif re.match(".+/vsearch/.+", url):
            return 4
        elif re.match(".+/pub/.+", url):
            return 5
        elif re.match(".+/in/.+", url):
            return 5
        return None

    def get_follow_links(self, level, hxs):
        if level in [1, 2, 3]:
            relative_urls = hxs.select("//ul[@class='directory']/li/a/@href").extract()
            relative_urls = ["http://nl.linkedin.com" + x for x in relative_urls]
            return relative_urls
        elif level == 4:
            relative_urls = hxs.select("//ol[@id='result-set']/li/h2/strong/a/@href").extract()
            #relative_urls = ["http://nl.linkedin.com" + x for x in relative_urls]
            return relative_urls

    def get_linkedin_id(self, url):
        find_index = url.find("linkedin.com/")
        if find_index >= 0:
            return url[find_index + 13:].replace('/', '-')
        return None

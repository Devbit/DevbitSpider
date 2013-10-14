# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class CrawlertestItem(Item):
    pass


class PersonProfileItem(Item):
    _id = Field()
    url = Field()
    name = Field()
    picture = Field()
    location = Field()
    sector = Field()
    summary = Field()
    specialities = Field()
    skills = Field()
    interests = Field()
    education = Field()
    groups = Field()
    honors = Field()
    courses = Field()
    experience = Field()
    overview_html = Field()
    languages = Field()

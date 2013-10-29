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


class VacatureItem(Item):
    _id = Field()
    source = Field()
    url = Field()
    title = Field()
    location = Field()
    company = Field()
    contact_person = Field()
    phone = Field()
    salary = Field()
    job_type = Field()
    hours = Field()
    education_level = Field()
    career_level = Field()
    date_created = Field()
    date_updated = Field()
    advert_html = Field()
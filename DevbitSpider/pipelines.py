# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy import log
from twisted.enterprise import adbapi
import MySQLdb.cursors


class CrawlertestPipeline(object):
    def process_item(self, item, spider):
        return item


# Copyright 2011 Julien Duponchelle <julien@duponchelle.info>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""MongoDB Pipeline for scrapy"""


MONGODB_SAFE = False
MONGODB_ITEM_ID_FIELD = "_id"


class MongoDBPipeline(object):
    def __init__(self, mongodb_server, mongodb_port, mongodb_db, mongodb_collection, mongodb_uniq_key,
                 mongodb_item_id_field, mongodb_safe):
        connection = pymongo.Connection(mongodb_server, mongodb_port)
        self.mongodb_db = mongodb_db
        self.db = connection[mongodb_db]
        self.mongodb_collection = mongodb_collection
        self.collection = self.db[mongodb_collection]
        self.uniq_key = mongodb_uniq_key
        self.itemid = mongodb_item_id_field
        self.safe = mongodb_safe

        if isinstance(self.uniq_key, basestring) and self.uniq_key == "":
            self.uniq_key = None

        if self.uniq_key:
            self.collection.ensure_index(self.uniq_key, unique=True)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('MONGODB_SERVER', 'localhost'), settings.get('MONGODB_PORT', 27017),
                   settings.get('MONGODB_DB', 'scrapy'), settings.get('MONGODB_COLLECTION', None),
                   settings.get('MONGODB_UNIQ_KEY', None), settings.get('MONGODB_ITEM_ID_FIELD', MONGODB_ITEM_ID_FIELD),
                   settings.get('MONGODB_SAFE', MONGODB_SAFE))

    def process_item(self, item, spider):
        if self.uniq_key is None:
            self.collection.insert(dict(item), safe=self.safe)
        else:
            log.msg(item)
            self.collection.update(
                            {self.uniq_key: item[self.uniq_key]},
                            dict(item),
                            upsert=True) 
            #result = self.collection.update({ self.uniq_key: item[self.uniq_key] }, { '$set': dict(item) },
            #                                upsert=True, safe=self.safe)

        log.msg("Item %s wrote to MongoDB database %s/%s" % (item['_id'], self.mongodb_db, self.mongodb_collection),
                level=log.DEBUG, spider=spider)
        return item

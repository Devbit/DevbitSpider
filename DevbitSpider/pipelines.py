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


class MySQLStorePipeline(object):

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                                            host='localhost',
                                            port=8032,
                                            db="linkedin_crawl",
                                            user="user",
                                            passwd="password",
                                            cursorclass=MySQLdb.cursors.DictCursor,
                                            charset='utf8',
                                            use_unicode=True
        )

    def process_item(self, item, spider):
        # run db query in thread pool
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist.
        # all this block run on it's own thread
        tx.execute("select * from entities where linkedin_id = %s", (item['_id'], ))
        result = tx.fetchone()
        if result:
            log.msg("Item already stored in db: %s" % item['_id'], level=log.DEBUG)
        else:
            #tx.execute(\
            #    "insert into sites (name, url, description, created) "
            #    "values (%s, %s, %s, %s)",
            #    (item['name'][0],
            #     item['url'][0],
            #     item['description'][0],
            #     time.time())
            #)
            tx.execute(
                "INSERT INTO entities (linkedin_id, linkedin_url, firstname, lastname, interest, location) "
                "values (%s, %s, %s, %s, %s, %s)",
                (
                    item.get('_id', "NULL"),
                    item.get('url', "NULL"),
                    item['name'].get('given_name', "NULL"),
                    item['name'].get('family_name', "NULL"),
                    item.get('interests', "NULL"),
                    item.get('locality', "NULL")
                )
            )
            tx.execute(
                "SELECT entity_id FROM entities WHERE linkedin_id = %s", (item.get('_id'), )
            )
            result = tx.fetchone()
            entity_key = result['entity_id']
            tx.execute(
                "INSERT INTO applicants (entity_id, sector, summary, overview_html) "
                "values (%s, %s, %s, %s)",
                (
                    entity_key,
                    item.get('industry', "NULL"),
                    item.get('summary', "NULL"),
                    item.get('overview_html', "NULL")
                )
            )
            tx.execute(
                "SELECT applicant_id FROM applicants WHERE entity_id = %s", (entity_key, )
            )
            result = tx.fetchone()
            applicant_key = result['applicant_id']
            for x in item.get('experience', []):
                now = 0
                if x.get('end', "NULL") == "Present":
                    now = 1
                tx.execute(
                    "INSERT INTO experience (experience_applicant_id, company, function, start, end, current, detail, description) "
                    "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        applicant_key,
                        x.get('org', "NULL"),
                        x.get('title', "NULL"),
                        x.get('start', "NULL"),
                        x.get('end', "NULL"),
                        now,
                        x.get('details', "NULL"),
                        x.get('desc', "NULL")
                    )
                )

            for x in item.get('education', []):
                tx.execute(
                    "INSERT INTO education (education_applicant_id, start, end, school, degree, major, description) "
                    "values (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        applicant_key,
                        x.get('start', "NULL"),
                        x.get('end', "NULL"),
                        x.get('name', "NULL"),
                        x.get('degree', "NULL"),
                        x.get('major', "NULL"),
                        x.get('desc', "NULL")
                    )
                )

            for x in item.get('courses', []):
                tx.execute(
                    "INSERT INTO courses (courses_applicant_id, name, organisation) "
                    "values (%s, %s, %s)",
                    (
                        applicant_key,
                        x.get('title', "NULL"),
                        x.get('org', "NULL"),
                    )
                )
                tx.execute(
                    "SELECT course_id FROM courses WHERE courses_applicant_id = %s", (applicant_key, )
                )
                result = tx.fetchone()
                course_key = result['course_id']
                for y in x.get('competency', []):
                    tx.execute(
                        "INSERT INTO competences (competences_course_id, name) "
                        "values (%s, %s)",
                        (
                            course_key,
                            y
                        )
                    )

            for x in item.get('skills', []):
                tx.execute(
                    "INSERT INTO skills (skills_applicant_id, name) "
                    "values (%s, %s)",
                    (
                        applicant_key,
                        x
                    )
                )

            for x in item.get('honors', []):
                tx.execute(
                    "INSERT INTO honors (honors_applicant_id, name) "
                    "values (%s, %s)",
                    (
                        applicant_key,
                        x
                    )
                )

            for x in item.get('languages', []):
                tx.execute(
                    "INSERT INTO languages (languages_applicant_id, name, level) "
                    "values (%s, %s, %s)",
                    (
                        applicant_key,
                        x.get('name', "NULL"),
                        x.get('level', "NULL")
                    )
                )

            groups = item.get('groups', {})
            for x in groups.get('groups', []):
                tx.execute(
                    "INSERT INTO groups (groups_applicant_id, name) "
                    "values (%s, %s)",
                    (
                        applicant_key,
                        x
                    )
                )

            for x in groups.get('organisations', []):
                tx.execute(
                    "INSERT INTO organisations (organisations_applicant_id, name) "
                    "values (%s, %s)",
                    (
                        applicant_key,
                        x
                    )
                )
            log.msg("Item stored in db: %s" % item['_id'], level=log.DEBUG)

    def handle_error(self, e):
        log.err(e)

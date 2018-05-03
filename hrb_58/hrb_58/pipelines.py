# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import cx_Oracle as oracle

class Hrb58Pipeline(object):
    def process_item(self, item, spider):
        return item
class OraclePipeline(object):
    def __init__(self, oracle_uri):
        self.oracle_uri = oracle_uri
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            oracle_uri=crawler.settings.get('ORACLE_URI'),
        )
    def open_spider(self, spider):
        self.connect = oracle.connect(self.oracle_uri)
    def close_spider(self, spider):
        self.connect.close()
    def process_item(self, item, spider):
        self.cursor = self.connect.cursor()
        sql = "insert into t_esf_58 {0}".format(tuple(item)).replace("'", "") + "values {0}".format(tuple(item.values()))
        self.cursor.execute(sql)
        self.connect.commit()
        # 提交sql语句
        return item




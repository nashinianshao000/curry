# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Hrb58ChuzuItem(scrapy.Item):
    # define the fields for your item here like:
    来源链接 = scrapy.Field()
    城市 = scrapy.Field()
    行政区 = scrapy.Field()
    片区 = scrapy.Field()
    题名 = scrapy.Field()
    发布时间 = scrapy.Field()
    租金 = scrapy.Field()
    付款方式 = scrapy.Field()
    租赁方式 = scrapy.Field()
    面积 = scrapy.Field()
    户型 = scrapy.Field()
    装修 = scrapy.Field()
    朝向 = scrapy.Field()
    楼层 = scrapy.Field()
    总层数 = scrapy.Field()
    小区 = scrapy.Field()
    区域 = scrapy.Field()
    地址 = scrapy.Field()
    联系人 = scrapy.Field()
    联系电话 = scrapy.Field()
    家具家电 = scrapy.Field()
    房屋亮点 = scrapy.Field()
    出租要求 = scrapy.Field()
    房源描述 = scrapy.Field()
    房屋图片 = scrapy.Field()


    # pass

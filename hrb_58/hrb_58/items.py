# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Hrb58Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    信息来源 = scrapy.Field()
    城市 = scrapy.Field()
    行政区 = scrapy.Field()
    片区 = scrapy.Field()
    来源链接 = scrapy.Field()
    题名 = scrapy.Field()
    小区名称 = scrapy.Field()
    小区链接 = scrapy.Field()
    地址 = scrapy.Field()
    建成年份 = scrapy.Field()
    # 房龄 = scrapy.Field()
    楼层 = scrapy.Field()
    总楼层 = scrapy.Field()
    当前层 = scrapy.Field()
    朝向 = scrapy.Field()
    建筑面积 = scrapy.Field()
    使用面积 = scrapy.Field()
    户型 = scrapy.Field()
    卧室数量 = scrapy.Field()
    客厅数量 = scrapy.Field()
    卫生间数量 = scrapy.Field()
    总价 = scrapy.Field()
    单价 = scrapy.Field()
    本月均价 = scrapy.Field()
    住宅类别 = scrapy.Field()
    产权性质 = scrapy.Field()
    装修情况 = scrapy.Field()
    联系人 = scrapy.Field()
    经纪公司 = scrapy.Field()
    电话号码 = scrapy.Field()
    发布时间 = scrapy.Field()
    # 小区总户数 = scrapy.Field()
    # 小区总建筑面积 = scrapy.Field()
    容积率 = scrapy.Field()
    楼盘绿化率 = scrapy.Field()
    楼盘物业费 = scrapy.Field()
    车位数量 = scrapy.Field()
    房屋图片 = scrapy.Field()
    数据来源 = scrapy.Field()
    # IP = scrapy.Field()
    # PID = scrapy.Field()













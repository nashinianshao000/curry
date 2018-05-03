# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import timedelta
import datetime
from hrb_58.items import Hrb58Item
import redis
import time
class SpiderHrbSpider(scrapy.Spider):
    name = 'spider_hrb'
    allowed_domains = ['58.com']
    start_urls = ['http://hrb.58.com/ershoufang/0/']
    db = redis.Redis(host="127.0.0.1", port=6379)
    def chuli_info(self, infos):
        # 处理字段无用符
        info = "".join(infos)
        return info.replace('\t', '').replace('\n', '').replace(' ', '')
    def chuli_time(self,fbtime):
        # 处理时间
        fbtimes = re.search('\d+(.*?)前',fbtime).group(1)
        if '秒' in fbtimes:
            timespan = timedelta(seconds=int(fbtime.replace('秒前', '')))
            fbtime = (datetime.datetime.now() - timespan).strftime('%Y-%m-%d %H:%M:%S')
        elif '分钟' in fbtimes:
            timespan = timedelta(minutes=int(fbtime.replace('分钟前', '')))
            fbtime = (datetime.datetime.now() - timespan).strftime('%Y-%m-%d %H:%M:00')
        elif '小时' in fbtimes:
            timespan = timedelta(hours=int(fbtime.replace('小时前', '')))
            fbtime = (datetime.datetime.now() - timespan).strftime('%Y-%m-%d %H:00:00')
        elif '天' in fbtimes:
            timespan = timedelta(days=int(fbtime.replace('天前', '')))
            fbtime = (datetime.datetime.now() - timespan).strftime('%Y-%m-%d 00:00:00')
        elif '今天' in fbtimes:
            fbtime = (datetime.datetime.now()).strftime('%Y-%m-%d 00:00:00')
        else :
            pass
        return fbtime
    def parse(self, response):
        content_urls = response.xpath('//ul[@class="house-list-wrap"]/li/div[@class="list-info"]/h2[@class="title"]/a[contains(@href,"http://hrb")]/@href').extract()
        lianxirens = response.xpath('//ul[@class="house-list-wrap"]/li/div[@class="list-info"]/h2[@class="title"]/a[contains(@href,"http://hrb")]/../../div[@class="jjrinfo"]/span[@class="jjrname-outer"]/text()').extract()
        i=0
        while i <len(content_urls):
            content_url = content_urls[i]
            lianxiren = lianxirens[i]
            i+=1
            if self.db.sismember("key_58_test",content_url):
                # redis判断url是否重复
                pass
            else:
                self.db.sadd("key_58_test",content_url)
                yield scrapy.Request(url=content_url,meta={'lianxiren':lianxiren},callback=self.get_item)
        # yield scrapy.Request(url=content_urls[0],meta={'lianxiren':lianxirens[0]},callback=self.get_item)
        # yield scrapy.Request(url=response.url,callback=self.parse)
    def get_item(self,response):
        # 解析详细页
        weizhi = response.xpath('//div[@class="nav-top-bar fl c_888 f12"]/a/text()').extract()
        weizhis = re.match('^(.*?)58同城(.*?)二手房(.*?)二手房',self.chuli_info(weizhi),re.S)
        try:
            chengshi = weizhis.group(1)
            xingzhengqu = weizhis.group(2)
            pianqu = weizhis.group(3)
        except:
            chengshi = ''
            xingzhengqu = ''
            pianqu = ''

        timing = response.xpath('//h1[@class="c_333 f20"]/text()').extract_first()

        try:
            xiaoqumingcheng = response.xpath('//div[@class="house-basic-right fr"]//span[@class="c_000 mr_10"]/a[@class="c_000"]/text()').extract_first()
            if xiaoqumingcheng == None:
                xiaoqumingcheng = response.xpath('//div[@class="house-basic-right fr"]/ul[@class="house-basic-item3"]/li/span[@class="c_000 mr_10"]/text()').extract_first()
                if xiaoqumingcheng == None:
                    xiaoqumingcheng = ''
        except:
            xiaoqumingcheng = ''
        try:
            xiaoqulianjie = 'http://hrb.58.com' + response.xpath('//div[@class="house-basic-right fr"]//span[@class="c_000 mr_10"]/a[@class="c_000"]/@href').extract_first()
        except:
            xiaoqulianjie = ''

        weizhi_content = response.xpath('//ul[@class="house-basic-item3"]//text()').extract()
        try:
            dizhi = re.findall('位置：(.*?)地图',self.chuli_info(weizhi_content))[0]
        except:
            dizhi = ''

        louceng = response.xpath('//div[@class="house-basic-right fr"]/div[@class="house-basic-item2"]/p[@class="room"]/span[@class="sub"]/text()').extract_first()

        huxing = response.xpath('//div[@class="house-basic-right fr"]/div[@class="house-basic-item2"]/p[@class="room"]/span[@class="main"]/text()').extract_first()
        try:
            zonglouceng = re.findall('共(\d+)层',louceng)[0]
        except:
            zonglouceng = ''
        try:
            dangqianceng = re.findall('^(.*?)/共',louceng)[0]
        except:
            dangqianceng = ''
        chaoxiang = response.xpath('//div[@class="house-basic-right fr"]/div[@class="house-basic-item2"]/p[@class="toward"]/span[@class="main"]/text()').extract_first()
        jianchengnianfen = response.xpath('//div[@class="house-basic-right fr"]/div[@class="house-basic-item2"]/p[@class="toward"]/span[@class="sub"]/text()').extract_first()
        jianzhumianji = response.xpath('//div[@class="house-basic-right fr"]/div[@class="house-basic-item2"]/p[@class="area"]/span[@class="main"]/text()').extract_first()
        zhuangxiuqingkuang = response.xpath('//div[@class="house-basic-right fr"]/div[@class="house-basic-item2"]/p[@class="area"]/span[@class="sub"]/text()').extract_first()
        huxingobj = re.search('^(\d+)室(\d+)厅(\d+)卫$',huxing)
        try:
            woshishuliang = huxingobj.group(1)
            ketingshuliang = huxingobj.group(2)
            weishengjianshuliang = huxingobj.group(3)
        except:
            woshishuliang = ''
            ketingshuliang = ''
            weishengjianshuliang = ''
        try:
            zongjia = self.chuli_info(response.xpath('//div[@class="house-basic-right fr"]/p[@class="house-basic-item1"]/span[@class="price"]//text()').extract())
        except:
            zongjia = ''
        try:
            danjia = self.chuli_info(response.xpath('//div[@class="house-basic-right fr"]/p[@class="house-basic-item1"]/span[@class="unit"]//text()').extract())
        except:
            danjia = ''
        feiyong = self.chuli_info(response.xpath('//ul[@class="general-item-left"]').extract())
        try:
            zhuzhaileibie = re.findall('房屋类型.*?class="c_000">(.*?)</span>',feiyong,re.S)[0]
        except:
            zhuzhaileibie = ''
        gaikuang = self.chuli_info(response.xpath('//div[@class="general-item-wrap"]/ul[@class="general-item-right"]').extract())
        try:
            canquanxingzhi = re.findall('产权年限.*?class="c_000">(.*?)</span>',gaikuang,re.S)[0]
        except:
            canquanxingzhi = ''
        dianhuahaoma = response.xpath('//div[@class="house-chat-phone"]/p[@class="phone-num"]/text()').extract_first()
        fabushijian = response.xpath('//div[@class="house-title"]/p[@class="house-update-info"]/span[@class="up"]/text()').extract_first()
        try:
            fabushijian = self.chuli_time(fabushijian)
        except:
            fabushijian = ''
        xiaoqu = self.chuli_info(response.xpath('//ul[@class="xiaoqu-desc"]').extract())
        try:
            rongjilv = re.findall('容积率.*?class="c_333">(.*?)</span>',xiaoqu,re.S)[0]
        except:
            rongjilv = ''
        try:
            loupanlvhualv = re.findall('绿化率.*?class="c_333">(.*?)</span>', xiaoqu, re.S)[0]
        except:
            loupanlvhualv = ''
        try:
            loupanwuyefei = re.findall('物业费.*?class="c_333">(.*?)</span>', xiaoqu, re.S)[0]
        except:
            loupanwuyefei = ''
        try:
            cheweishuliang = re.findall('车位信息.*?class="c_333">(.*?)</span>', xiaoqu, re.S)[0]
        except:
            cheweishuliang = ''
        try:
            xiaoqujunjia = re.findall('小区均价.*?class="c_333mr_20">(.*?)</span>', xiaoqu, re.S)[0]
        except:
            xiaoqujunjia = ''
        img_src = response.xpath('//div[@class="general-item-wrap"]/ul[@class="general-pic-list"]/li/img/@data-src').extract()
        try:
            fangwutupian = '|'.join(img_src)
        except:
            fangwutupian = ''
        item = Hrb58Item()
        item['信息来源'] = '58同城'
        item['城市'] = chengshi
        item['行政区'] = xingzhengqu
        item['片区'] = pianqu
        item['来源链接'] = response.url
        item['题名'] = timing
        item['小区名称'] = self.chuli_info(xiaoqumingcheng)
        item['小区链接'] = xiaoqulianjie
        item['地址'] = dizhi
        item['建成年份'] = jianchengnianfen
        # item['房龄'] =
        item['楼层'] = louceng
        item['总楼层'] = zonglouceng
        item['当前层'] = dangqianceng
        item['朝向'] = chaoxiang
        item['建筑面积'] = jianzhumianji
        # item['使用面积'] =
        item['户型'] = huxing
        item['卧室数量'] = woshishuliang
        item['客厅数量'] = ketingshuliang
        item['卫生间数量'] = weishengjianshuliang
        item['总价'] = zongjia
        item['单价'] = danjia
        item['本月均价'] = xiaoqujunjia
        item['住宅类别'] = zhuzhaileibie
        item['产权性质'] = canquanxingzhi
        item['装修情况'] = zhuangxiuqingkuang
        item['联系人'] = response.meta['lianxiren']
        item['经纪公司'] = '源房人个'
        item['电话号码'] = dianhuahaoma
        item['发布时间'] = fabushijian
        # item['小区总户数'] = xiaoqu
        # item['小区总建筑面积'] =
        item['容积率'] = rongjilv
        item['楼盘绿化率'] = loupanlvhualv
        item['楼盘物业费'] = loupanwuyefei
        item['车位数量'] = cheweishuliang
        item['房屋图片'] = fangwutupian
        item['数据来源'] = '58'
        yield item
        # item['IP'] =''
        # item['PID'] =''







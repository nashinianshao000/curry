# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from datetime import timedelta
import redis
from lxml import etree
import requests
import json
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from hrb_58_chuzu.items import Hrb58ChuzuItem
class phone58(object):
    AES_SECRET_KEY = b'crazycrazycrazy1'
    IV = 16 * b'\x00'

    @classmethod
    def decrypt(cls, text):
        cryptor = AES.new(cls.AES_SECRET_KEY, AES.MODE_CBC, IV=cls.IV)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.decode().strip("")  # replace(b'\x05',b'')

class SpiderHrbSpider(scrapy.Spider):
    name = 'spider_hrb'
    allowed_domains = ['58.com']
    start_urls = ['http://hrb.58.com/chuzu/0/']
    db = redis.Redis(host="127.0.0.1", port=6379)
    def parse(self, response):
        chengshi = response.url.split('.',1)[0]
        content_urls = response.xpath(
            '//ul[@class="listUl"]/li/div[@class="des"]/h2/a[contains(@href,"{}")]/@href'.format(chengshi)).extract()
        # lianxirens = response.xpath(
        #     '//ul[@class="listUl"]/li/div[@class="des"]/h2/a[contains(@href,"{}")]/../../p[@class="geren"]/text()'.format(chengshi)).extract()
        lianxirens = response.xpath('//ul[@class="listUl"]/li/div[@class="des"]/h2/a[contains(@href,"{}")]/../../p[@class="geren"]'.format(chengshi)).re('</span>：(.*?)</p>')
        # 访问app获取电话
        for content_url,lianxiren in zip(content_urls,lianxirens):
            if self.db.sismember("key_58_chuzu_test", content_url):
                # redis判断url是否重复
                pass
            else:
                self.db.sadd("key_58_chuzu_test", content_url)
                citycode = content_url.split('.')[0].replace('http://', '')
                tel1 = 'http://apphouse.58.com/api/detail/'
                tel2 = '?platform=1&version=1&v=1&format=json&sidDict=%7B%22PGTID%22%3A%22%22%2C%22GTID%22%3A%22181997156196609718361274590%22%7D&localname=' + citycode + '&signature=f065ef8ae8a0f971d7f0bd06642f7'
                telurl = tel1 + content_url.split('/')[-2] + '/' + content_url.split('/')[-1].replace('x.shtml', '') + tel2
                yield scrapy.Request(url=telurl,meta={'content_url':content_url,'lianxiren':lianxiren},callback=self.get_appjson,encoding='utf-8')
        # test_url = 'http://apphouse.58.com/api/detail/hezu/33887579483470?platform=1&version=1&v=1&format=json&sidDict=%7B%22PGTID%22%3A%22%22%2C%22GTID%22%3A%22181997156196609718361274590%22%7D&localname=hrb&signature=f065ef8ae8a0f971d7f0bd06642f7'
        # yield scrapy.Request(url=test_url,callback=self.get_appjson,encoding='utf-8')


        # for content_url, lianxiren in zip(content_urls, lianxirens):
        #     lianxiren = lianxiren.replace(' ','')
        #     if self.db.sismember("key_58_chuzu_test", content_url):
        #         # redis判断url是否重复
        #         pass
        #     else:
        #         self.db.sadd("key_58_chuzu_test", content_url)
        #         yield scrapy.Request(url=content_url, meta={'lianxiren': lianxiren}, callback=self.get_item)
    def get_appjson(self,response):
        content_url = response.meta['content_url']
        lianxiren = response.meta['lianxiren']

        a = json.loads(response.text,encoding='utf-8')
        # print(a)
        # for i in a['result']['info']:
        #     try:
        #         print(i)
        #         phonenum = i['linkman_area']['tel_info']['dial_info']['action']['phonenum']
        #         print(phonenum)
        #
        #     except:
        #         pass
        try:
            phonenums = a['result']['info'][-1]['linkman_area']['tel_info']['dial_info']['action']['phonenum']
            phonenum = phone58.decrypt(phonenums)

        except:
            phonenum = ''
        yield scrapy.Request(url=content_url, meta={'phonenum': phonenum,'lianxiren':lianxiren}, callback=self.get_item)

        #     print(i)
            # pass
            # for j in i['linkman_area']:
            #     print(j)
        # print(response.text,encoding='utf-8')
        # try:
        #     rTT = response.decode('utf-8')
        #     lr[metadatas[40]] = phone58.decrypt(re.search('"phonenum":"(.*?)"', rTT).group(1))
        # except:
        #     infoID = urlbase.url.split("/")[-1].replace("x.shtml", "")
        #     list_name = "zufang" if lr[metadatas[11]] == "整租" else "hezu"
        #     full_path = "1,8" if lr[metadatas[11]] == "整租" else "1,10"
        #     lr[metadatas[
        #         40]] = "http://app.58.com/api/windex/scandetail/car/%s/?pid=798&jumptype=native&wlmode=qr&pagetype=detail&infoID=%s&list_name=%s&local_name=%s&topcate=house&full_path=%s" \
        #                % (infoID, infoID, list_name, urlbase.url.split('.')[0].replace('http://', ''), full_path)
        #     pass
    def get_item(self,response):
        weizhi = response.xpath('//div[@class="nav-top-bar fl c_888 f12"]/a/text()').extract()
        weizhis = re.search('58同城(.*?)租房(.*?)租房(.*?)租房', self.chuli_info(weizhi), re.S)
        if weizhis == None:
            weizhis = re.search('58同城(.*?)租房(.*?)租房', self.chuli_info(weizhi), re.S)
        try:
            chengshi = weizhis.group(1).replace('合','')
        except:
            chengshi = ''
        try:
            xingzhengqu = weizhis.group(2).replace('合','')
        except:
            xingzhengqu = ''
        try:
            pianqu = weizhis.group(3).replace('合','')
        except:
            pianqu = ''
        timing = response.xpath('//h1[@class="c_333 f20"]/text()').extract_first()
        fabushijian = response.xpath(
            '//div[@class="house-title"]/p[@class="house-update-info c_888 f12"]/text()').extract_first()
        try:
            fabushijian = self.chuli_time(self.chuli_info(fabushijian))
        except:
            fabushijian = ''
        try:
            zujins = response.xpath('//div[@class="house-pay-way f16"]/span[@class="c_ff552e"]//text()').extract()
            zujin = self.chuli_info(zujins)
        except:
            zujin = ''
        fukuanfangshi = response.xpath('//div[@class="house-pay-way f16"]/span[@class="c_333"]/text()').extract_first()
        if fukuanfangshi == None:
            fukuanfangshi = ''
        content_infos = self.chuli_info(response.xpath('//div[@class="house-desc-item fl c_333"]/ul[@class="f14"]').extract())

        zulinfangshi = self.chuli_re(re.findall('租赁方式：</span><span>(.*?)</span>',content_infos))
        fangwuleixing = self.chuli_re(re.findall('房屋类型：</span><span>(.*?)</span>',content_infos))
        caoxianglouceng = self.chuli_re(re.findall('朝向楼层：</span><span>(.*?)</span>', content_infos))
        suozaixiaoqu = self.chuli_re(re.findall('所在小区：</span><span>.*?>(.*?)</a></span>', content_infos))
        suoshuquyus = self.chuli_re(re.findall('所属区域：</span><span>.*?>(.*?)</a>.*?>(.*?)</a></span>.*?详细地址', content_infos))
        if suoshuquyus == []:
            suoshuquyu = self.chuli_re(re.findall('所属区域：</span><span>.*?>(.*?)</a>.*?详细地址', content_infos))
        else:
            suoshuquyu = '-'.join(suoshuquyus)
        xiangxidizhi = self.chuli_re(re.findall('详细地址：</span><span.*?>(.*?)</span>', content_infos))
        mianji = self.chuli_re(re.findall('(\d+平)',fangwuleixing))
        huxing = self.chuli_re(re.findall('(\d室\d厅\d卫)',fangwuleixing))
        zhuangxiu = self.chuli_re(re.findall('(..装修)',fangwuleixing))
        caoxiang = self.chuli_re(re.findall('^(.*?).层',caoxianglouceng))
        louceng = self.chuli_re(re.findall('(.层)/',caoxianglouceng))
        zonglouceng = self.chuli_re(re.findall('/(共\d+层)$',caoxianglouceng))
        lianxiren = response.meta['lianxiren']
        fangwupeizhis = response.xpath('//div[@class="main-detail-info fl"]/ul[@class="house-disposal"]/li/text()').extract()
        if fangwupeizhis == None:
            fangwupeizhi = ''
        else:
            fangwupeizhi = '-'.join(fangwupeizhis)
        fangwuliangdians = self.chuli_info(response.xpath('//div[@class="house-word-introduce f16 c_555"]/ul[@class="introduce-item"]').extract())
        fangwuliangdian = self.chuli_info(re.findall('>房屋亮点</span><spanclass="a2"><em>(.*?)</em></span>',fangwuliangdians))
        chuzuyaoqiu = self.chuli_info(re.findall('>出租要求</span><spanclass="a2"><em>(.*?)</em></span>',fangwuliangdians))
        fangyuanmiaoshus = self.chuli_re(re.findall('>房源描述</span><spanclass="a2">(.*?)</span></li>',fangwuliangdians))
        fangyuanmiaoshu = fangyuanmiaoshus.replace('<p>', '').replace('</p>', '').replace('<span>', '').replace('<strong>', '').replace('</span>', '').replace('</strong>', '')
        fangwutupians = response.xpath('//ul[@class="house-pic-list "]/li/img/@lazy_src').extract()
        if fangwutupians == None:
            fangwutupian =''
        else:
            fangwutupian = '|'.join(fangwutupians)
        phonenum = response.meta['phonenum']
        if phonenum == '':
            infoID = response.url.split("/")[-1].replace("x.shtml", "")
            list_name = "zufang" if zulinfangshi == "整租" else "hezu"
            full_path = "1,8" if zulinfangshi == "整租" else "1,10"
            phonenum = "http://app.58.com/api/windex/scandetail/car/%s/?pid=798&jumptype=native&wlmode=qr&pagetype=detail&infoID=%s&list_name=%s&local_name=%s&topcate=house&full_path=%s" \
                       % (infoID, infoID, list_name, response.url.split('.')[0].replace('http://', ''), full_path)
        item = Hrb58ChuzuItem()
        item['来源链接'] =response.url
        item['城市'] =chengshi
        item['行政区'] =xingzhengqu
        item['片区'] =pianqu
        item['题名'] =timing
        item['发布时间'] =fabushijian
        item['租金'] =zujin
        item['付款方式'] =fukuanfangshi
        item['租赁方式'] =zulinfangshi
        item['面积'] =mianji
        item['户型'] =huxing
        item['装修'] =zhuangxiu
        item['朝向'] =caoxiang
        item['楼层'] =louceng
        item['总层数'] =zonglouceng
        item['小区'] =suozaixiaoqu
        item['区域'] =suoshuquyu
        item['地址'] =xiangxidizhi
        item['联系人'] =lianxiren.replace(' ','')
        item['联系电话'] =phonenum
        item['家具家电'] =fangwupeizhi
        item['房屋亮点'] =fangwuliangdian
        item['出租要求'] =chuzuyaoqiu
        item['房源描述'] =fangyuanmiaoshu
        item['房屋图片'] = fangwutupian
        yield item
    def chuli_re(self,arg):
        if arg != []:
            arg = arg[0]
        if arg == []:
            arg = ''
        return arg

    def chuli_info(self, infos):
        # 处理字段无用符
        info = "".join(infos)
        return info.replace('\t', '').replace('\n', '').replace(' ', '').replace('\xa0', '').replace('</em><em>', '-')

    def chuli_time(self, fbtime):
        # 处理时间
        try:
            fbtimes = re.search('\d+(.*?)前', fbtime).group(1)
        except:
            s = re.findall('\d\d-\d\d',fbtime)[0]
            if fbtime == s:
                fbtime = '2018-'+s+' 00:00:00'
                fbtimes = ''
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
        else:
            pass
        return fbtime
















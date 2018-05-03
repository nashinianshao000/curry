import time
import os

while True:
    os.system("scrapy crawl spider_hrb")
    time.sleep(60)  #每隔60s运行一次
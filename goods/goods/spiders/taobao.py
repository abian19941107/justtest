# -*- coding: utf-8 -*-
import scrapy


class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['taobo.com']
    start_urls = ['http://www.taobo.com/']

    def parse(self, response):
        pass

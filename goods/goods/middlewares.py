# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from logging import getLogger

import time
from selenium.webdriver import Chrome

from fake_useragent import UserAgent
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class GoodsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class GoodsDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UserAgentMiddleware(object):
    '''
    设置user_agent
    支持在在settings中设置随机ua的类型
    '''
    def __init__(self, ua_type):
        self.user_agent = UserAgent()
        self.ua_type = ua_type

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings.get('USER_AGENT_TYPE'))
        return o

    def process_request(self, request, spider):
        if self.ua_type:
            usa_agent = getattr(self.user_agent,self.ua_type,'scrapy')
            request.headers.setdefault(b'User-Agent', usa_agent)

class SeleniumMiddleware(object):
    def __init__(self,timeout = 10,load_image = False):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.option = Options()
        # 无界面运行
        self.option.add_argument('--headless')
        self.option.add_argument('--disable-gpu')
        # 不加载图片
        self.load_image = load_image
        if self.load_image:
            self.option.add_experimental_option('prefs',{"profile.managed_default_content_settings.images":2})
        self.driver=Chrome(
            executable_path='D:\selenium_webdriver\chromedriver.exe',
            chrome_options=self.option
        )
        self.driver.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.driver,25)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('SELENIUM_TIMEOUT'),
            crawler.settings.get('LOAD_IMAGE'),
                   )

    def process_request(self, request, spider):
        '''
        使用chrome 抓取渲染页面
        :param request: scrapy Request请求对象
        :param spider: Spider对象
        :return: 返回 HtmlResponse对象
        '''
        # 判断是否需要使用selenium
        if not request.meta.get('useSelenium',False):
            return None
        try:
            self.driver.get(request.url)
            # 是否使用搜索框
            if request.meta.get('selection',False):
                selection = self.wait.until(
                   expected_conditions.presence_of_element_located((By.XPATH,'//input[@id="q"]'))
                )
                selection.clear()
                selection.send_keys(request.meta.get('selection'))
                selection.send_keys(Keys.ENTER)
            # 等待页面加载完成
            self.wait.until(
                expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, '//div[@id="mainsrp-pager"]|//div[@id="mainsrp-itemlist"]'))
            )
            response = HtmlResponse(url=request.url,request=request,status=200,encoding='utf-8',body=self.driver.page_source)
        except:
            response = HtmlResponse(url=request.url,request=request,status=500)
        return response
import json
from utils import get_page
from pyquery import PyQuery as pq
from db import RedisClient

POOL_THRESHOLD = 10000

# 元类
class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)

# 抓取器类
class Crawler(object,metaclass=ProxyMetaclass):
    def crawl_daili66(self, page_count=6):
        for page in range(1, page_count+1):
            url = 'http://www.66ip.cn/{}.html'.format(page)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr('td:nth-child(1)').text()
                    port = tr('td:nth-child(2)').text()
                    yield ':'.join([ip,port])

    def crawl_ip3366(self, page_count=6):
        for page in range(1, page_count+1):
            url = 'http://www.ip3366.net/free/?stype=1&page={}'.format(page)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.table tbody tr').items()
                for tr in trs:
                    ip = tr('td:nth-child(1)').text()
                    port = tr('td:nth-child(2)').text()
                    yield ':'.join([ip,port])

    def crawl_kuaidaili(self, page_count=6):
        for page in range(1, page_count+1):
            url = 'http://www.kuaidaili.com/free/inha/{}/'.format(page)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.table tbody tr').items()
                for tr in trs:
                    ip = tr('td:nth-child(1)').text()
                    port = tr('td:nth-child(2)').text()
                    yield ':'.join([ip,port])

# 获取器类
class Getter(object):
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        if self.redis.count() >= POOL_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('获取器开始执行!')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                for proxy in eval('self.crawler.{}()'.format(callback)):
                    self.redis.add(proxy)                    

if __name__ == '__main__':
    g = Getter()
    g.run()
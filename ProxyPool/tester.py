import asyncio
import aiohttp
import time
from db import RedisClient

VALID_STATUS_CODES = [200]
TEST_URL = 'http://www.baidu.com'
BATCH_TEST_SIZE = 10

class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self,proxy):
        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15, allow_redirects=False) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                    else:
                        self.redis.decrease(proxy)
            except (aiohttp.ClientError, aiohttp.client_exceptions.ClientConnectorError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)

    def run(self):
        print('测试器开始运行！')
        try:
            proxies = self.redis.all()
            count = len(proxies)
            print('当前共有{0}个代理'.format(count))
            for i in range(0, count, BATCH_TEST_SIZE):
                start = i
                end = min(i+BATCH_TEST_SIZE, count)
                test_proxies = proxies[start:end]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误',e.args)

if __name__ == '__main__':
    t = Tester()
    t.run()
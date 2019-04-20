import redis
from random import choice
import re

MAX_SCORE = 100 #最大分数
MIN_SCORE = 0
INITIAL_SCORE = 10 #初始分数
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = 'foobared'
REDIS_KEY = 'proxies' #有序集合的键名

class RedisClient(object):
    def __init__(self,host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD):
        self.db = redis.StrictRedis(host=host,port=port,password=password,decode_responses=True)

    # 添加代理
    def add(self,proxy,score=INITIAL_SCORE):
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+',proxy):
            print('{0}不符合规范，丢弃！'.format(proxy))
            return
        if not self.db.zscore(REDIS_KEY,proxy):
            print('代理{0}添加成功'.format(proxy))
            return self.db.zadd(REDIS_KEY,{proxy:score})           

    # 随机获取有效代理
    def random(self):
        result = self.db.zrangebyscore(REDIS_KEY,MAX_SCORE,MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY,0,100)
            if len(result):
                return choice(result)
            else:
                print('代理池已枯竭！')
                return

    # 代理的减分与删除
    def decrease(self,proxy):
        score = self.db.zscore(REDIS_KEY,proxy)
        if score:
            if score > MIN_SCORE:
                print('{0}的当前分数为{1}；减1'.format(proxy,score))
                return self.db.zincrby(REDIS_KEY,-1,proxy)
            else:
                print('{0}的当前分数为{1}；移除'.format(proxy,score))
                return self.db.zrem(REDIS_KEY,proxy)

    # 判断代理是否存在
    def exists(self,proxy):
        if self.db.zscore(REDIS_KEY,proxy):
            return True
        else:
            return False

    # 将代理分数设置为最大值
    def max(self,proxy):
        print('代理{0}可用，设置分数为{1}'.format(proxy,MAX_SCORE))
        return self.db.zadd(REDIS_KEY,MAX_SCORE,proxy)

    # 获取代理数量
    def count(self):
        return self.db.zcard(REDIS_KEY)

    # 获取全部代理
    def all(self):
        return self.db.zrangebyscore(REDIS_KEY,MIN_SCORE,MAX_SCORE)

if __name__ == '__main__':
    conn = RedisClient()
    result = conn.count()
    print(result)
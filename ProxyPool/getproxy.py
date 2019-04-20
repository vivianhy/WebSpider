from db import RedisClient

def get_proxy():
    conn = RedisClient()
    return conn.random()

if __name__ == '__main__':
    result = get_proxy()
    print(result)
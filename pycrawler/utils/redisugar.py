__author__ = 'mengpeng'
import redis
from pycrawler.exception import PyCrawlerException


class RediSugar(object):
    Pool = None

    @staticmethod
    def getConnection():
        if not RediSugar.Pool:
            RediSugar.Pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=RediSugar.Pool)
        try:
            r.ping()
            return r
        except redis.ConnectionError:
            raise PyCrawlerException('Connect to redis server failed')
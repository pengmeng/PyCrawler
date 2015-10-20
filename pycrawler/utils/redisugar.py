# -*- coding: utf-8 -*-
# This file will be replace with redisugar project
# Current code only here to make the whole project run
__author__ = 'mengpeng'
import redis


class RediSugarException(Exception):
    pass


class RediSugar(object):
    _Pool = None

    @staticmethod
    def getSugar(host='localhost', port=6379, db=0):
        if not RediSugar._Pool:
            RediSugar._Pool = redis.ConnectionPool(host=host, port=port, db=db)
        r = redis.Redis(connection_pool=RediSugar._Pool)
        try:
            return r.ping() and RediSugar(r)
        except redis.ConnectionError:
            raise RediSugarException('Connect to redis server failed')

    def __init__(self, _redis):
        self.redis = _redis

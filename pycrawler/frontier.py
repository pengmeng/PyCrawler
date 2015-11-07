# -*- coding: utf-8 -*-
__author__ = 'mengpeng'
import re
from pybloom import ScalableBloomFilter
from pycrawler.exception import FrontierException
from pycrawler.utils.redisugar import RediSugar
from redis.exceptions import ResponseError


class Frontier(object):
    Dict = {}

    def __init__(self):
        pass

    @staticmethod
    def register(cls):
        if isinstance(cls, type):
            Frontier.Dict[cls.__name__] = cls
            return cls
        else:
            raise FrontierException('Must register Frontier with class name')

    @staticmethod
    def get(name):
        if name in Frontier.Dict:
            return Frontier.Dict[name]
        else:
            raise FrontierException('No Frontier class named '+name)

    def setargs(self, args):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def visitednum(self):
        raise NotImplementedError

    def add(self, item):
        raise NotImplementedError

    def next(self, *args):
        raise NotImplementedError

    def hasnext(self):
        raise NotImplementedError

    def isVisited(self, item):
        raise NotImplementedError

    def validate(self, item):
        raise NotImplementedError

    def clean(self, *args):
        raise NotImplementedError


@Frontier.register
class BFSFrontier(Frontier):
    def __init__(self, spider):
        super(BFSFrontier, self).__init__()
        self._spider = spider
        self.args = {'rules': [],
                     'order': 'bfs'}
        self.redis = RediSugar.getSugar().redis
        self.filter = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        self.todo = spider.name + '-todo'
        self.visited = spider.name + '-visited'
        self._feedfilter()

    def setargs(self, args):
        if not isinstance(args, dict):
            raise FrontierException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value
        if self.args['rules']:
            for each in self.args['rules']:
                try:
                    re.compile(each)
                except re.error:
                    raise FrontierException('Wrong regular expression: \'{0}\''.format(each))

    def __len__(self):
        return self.redis.llen(self.todo)

    def __contains__(self, item):
        temp = self.redis.lrange(self.todo, 0, self.__len__())
        return item in temp

    def visitednum(self):
        return self.redis.llen(self.visited)

    def add(self, item, force=False):
        if isinstance(item, list):
            for each in iter(item):
                self._addone(each, force)
        elif isinstance(item, str):
            self._addone(item, force)
        else:
            raise FrontierException('Unsupported type: {0}'.format(type(item)))

    def _addone(self, item, force=False):
        if force:
            self.redis.rpush(self.todo, item)
        elif not self.isVisited(item) and self.validate(item):
            self.redis.rpush(self.todo, item)

    def next(self, num=1):
        if num == 1:
            return [self._nextone()]
        elif num == 0 or num >= self.__len__():
            return self._nextall()
        elif num > 1:
            result = []
            while len(result) < num:
                item = self._nextone()
                if item:
                    result.append(item)
            return result
        else:
            raise FrontierException('Num should be greater than 0')

    def _nextone(self):
        item = self.redis.lpop(self.todo)
        # while item:
        #     if item in self.filter:
        #         item = self.redis.lpop(self.todo)
        #     else:
        self.filter.add(item)
        self.redis.rpush(self.visited, item)
        #         break
        return item

    def _nextall(self):
        temp = self.redis.lrange(self.todo, 0, self.__len__())
        result = [x for x in temp if x not in self.filter]
        self.redis.ltrim(self.todo, len(temp), self.__len__())
        for each in iter(result):
            self.filter.add(each)
            self.redis.rpush(self.visited, each)
        return result

    def hasnext(self):
        return self.__len__() != 0

    def isVisited(self, item):
        return item in self.filter

    def validate(self, item):
        if self.args['rules']:
            for each in self.args['rules']:
                if not re.match(each, item):
                    return False
        return True

    def clean(self, *args):
        if 'visited' in args:
            self.redis.delete(self.visited)
        if 'todo' in args:
            self.redis.delete(self.todo)

    def _feedfilter(self):
        length = self.redis.llen(self.visited)
        if length != 0:
            map(self.filter.add, self.redis.lrange(self.visited, 0, length))

    def save(self):
        try:
            self.redis.bgsave()
        except ResponseError:
            pass

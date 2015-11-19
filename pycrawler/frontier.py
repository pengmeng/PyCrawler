# -*- coding: utf-8 -*-
from pybloom import ScalableBloomFilter
from pycrawler.exception import FrontierException
from pycrawler.utils.redisugar import RediSugar
from redis.exceptions import ResponseError


class Frontier(object):
    Dict = {}

    def __init__(self):
        self.args = None

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
        if not isinstance(args, dict):
            raise FrontierException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value

    def __len__(self):
        raise NotImplementedError

    def add(self, item):
        raise NotImplementedError

    def next(self, *args):
        raise NotImplementedError

    def hasnext(self):
        raise NotImplementedError

    def clean(self, *args):
        raise NotImplementedError


@Frontier.register
class BFSFrontier(Frontier):
    def __init__(self, spider):
        super(BFSFrontier, self).__init__()
        self._spider = spider
        self.redis = RediSugar.getSugar().redis
        self.filter = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        self.queue_set = {'todo', 'visited', 'failed'}
        self.todo = spider.name + '-todo'
        self.force = spider.name + '-force'
        self.visited = spider.name + '-visited'
        self.failed = spider.name + '-failed'
        self.args = {'enable_filter': True}
        self._feedfilter()

    def __len__(self):
        return self.redis.llen(self.todo) + self.redis.llen(self.force)

    def count(self, queue_name):
        if queue_name not in self.queue_set:
            raise FrontierException('Only support queue names: ' + ' '.join(self.queue_set))
        elif queue_name == 'todo':
            return self.__len__()
        else:
            return self.redis.llen(self._spider.name + '-' + queue_name)

    def add(self, item, force=False):
        if isinstance(item, list):
            for each in iter(item):
                self._addone(each, force)
        elif isinstance(item, str):
            self._addone(item, force)
        else:
            raise FrontierException('Unsupported type: {0}'.format(type(item)))

    def _addone(self, item, force):
        if not self.args['enable_filter']:
            self.redis.rpush(self.todo, item)
        elif force:
            self.redis.rpush(self.force, item)
        elif item not in self.filter:
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
                if not item:
                    break
                result.append(item)
            return result
        else:
            raise FrontierException('Num should be greater than 0')

    def _nextone(self):
        item = self.redis.lpop(self.force)
        if item:
            return item
        else:
            item = self.redis.lpop(self.todo)
        while item and self.args['enable_filter']:
            if item not in self.filter:
                break
            item = self.redis.lpop(self.todo)
        self.filter.add(item)
        self.redis.rpush(self.visited, item)
        return item

    def _nextall(self):
        result = self.redis.lrange(self.force, 0, -1)
        self.redis.ltrim(self.force, len(result), self.redis.llen(self.force))
        temp = self.redis.lrange(self.todo, 0, self.__len__())
        if self.args['enable_filter']:
            temp = [x for x in temp if x not in self.filter]
        result += temp
        self.redis.ltrim(self.todo, len(temp), self.redis.llen(self.todo))
        for each in iter(temp):
            self.filter.add(each)
            self.redis.rpush(self.visited, each)
        return result

    def hasnext(self):
        return self.__len__() != 0

    def clean(self, *args):
        if 'visited' in args:
            self.redis.delete(self.visited)
        if 'todo' in args:
            self.redis.delete(self.todo)
            self.redis.delete(self.force)
        if 'failed' in args:
            self.redis.delete(self.failed)

    def _feedfilter(self):
        if self.redis.llen(self.visited):
            for each in iter(self.redis.lrange(self.visited, 0, -1)):
                self.filter.add(each)

    def add_to_fail(self, item):
        if isinstance(item, list):
            for each in iter(item):
                self.redis.rpush(self.failed, each)
        elif isinstance(item, str):
            self.redis.rpush(self.failed, item)
        else:
            raise FrontierException('Unsupported type: {0}'.format(type(item)))

    def get_all_fail(self, item):
        return self.redis.lrange(self.failed, 0, -1)

    def recover_fail(self):
        while self.redis.llen(self.failed) != 0:
            self.redis.rpoplpush(self.failed, self.force)

    def save(self):
        try:
            self.redis.bgsave()
        except ResponseError:
            pass

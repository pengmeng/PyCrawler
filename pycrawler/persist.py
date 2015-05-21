__author__ = 'mengpeng'
from mongojuice.mongo import Mongo
from mongojuice.document import Document
from pycrawler.exception import PersistException


class Item(Document):
    def __init__(self):
        super(Item, self).__init__()

    def persistable(self):
        raise NotImplementedError


class Persist(object):
    Dict = {}

    def __init__(self, spider):
        pass

    @staticmethod
    def register(cls):
        if isinstance(cls, type):
            Persist.Dict[cls.__name__] = cls
            return cls
        else:
            raise PersistException('Must register Persist with class name')

    @staticmethod
    def getPersist(name):
        if name in Persist.Dict:
            return Persist.Dict[name]
        else:
            raise PersistException('No Persist class named '+name)

    def __len__(self):
        raise NotImplementedError

    def setargs(self, args):
        raise NotImplementedError
    
    def save(self, *args):
        raise NotImplementedError


@Persist.register
class MongoPersist(Persist):
    def __init__(self, spider):
        super(MongoPersist, self).__init__(spider)
        self._spider = spider
        self.args = {'db': 'pycrawler',
                     'collection': spider.name+'-items'}
        self.mongo = Mongo('pycrawler', spider.name+'-items')

    def setargs(self, args):
        if not isinstance(args, dict):
            raise PersistException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value
        self.mongo.database = self.args['db']
        self.mongo.collection = self.args['collection']

    def __len__(self):
        return self.mongo.count()

    def save(self, items):
        try:
            if isinstance(items, list):
                try:
                    items = [x.tomongo() for x in items]
                    map(self.mongo.insert, items)
                except AttributeError:
                    raise PersistException('Items must implement tomongo()')
            else:
                try:
                    self.mongo.insert(items.tomongo())
                except AttributeError:
                    raise PersistException('Items must implement tomongo()')
        except (AttributeError, TypeError) as e:
            raise PersistException('Database error: '+e.message)

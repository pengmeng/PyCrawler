__author__ = 'mengpeng'
import pymongo
from pymongo.errors import DuplicateKeyError


class MongoJuice(object):

    Host = 'localhost'
    Port = 27017
    Client = None

    @staticmethod
    def config(param):
        try:
            MongoJuice.Host = param['host']
            MongoJuice.Port = param['port']
        except KeyError:
            print('Unvalid configuration dict.')

    def __init__(self, db_name, coll_name):
        if not MongoJuice.Client:
            MongoJuice.Client = pymongo.MongoClient(MongoJuice.Host, MongoJuice.Port)
        self.db_name = db_name
        self.coll_name = coll_name
        self._db = MongoJuice.Client[db_name]
        self._coll = self.db[coll_name]

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, value):
        self.db_name = value
        self._db = MongoJuice.Client[self.db_name]

    @property
    def coll(self):
        return self._coll

    @coll.setter
    def coll(self, value):
        self.coll_name = value
        self._coll = self.db[value]

    def insert(self, items, overwrite=True):
        if isinstance(items, dict):
            if overwrite:
                self._coll.save(items)
            else:
                try:
                    self._coll.insert(items)
                except DuplicateKeyError:
                    raise AttributeError('_id is already in {0}'.format(self.coll_name))
        else:
            raise TypeError('Inserting item must be a dict.')

    def findone(self, query=None):
        return self._coll.find_one(spec_or_id=query)

    def find(self, query=None, limit=0, sort=None, skip=0):
        return self._coll.find(spec=query, limit=limit, sort=sort, skip=skip)

    def likefindone(self, key, likevalue):
        query = {key: {'$regex': likevalue}}
        return self._coll.find_one(spec_or_id=query)

    def count(self):
        return self._coll.count()

    def remove(self, query):
        self._coll.remove(query)
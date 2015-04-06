__author__ = 'mengpeng'
from unittest import TestCase
from test_scraper import SpiderTest
from pycrawler.exception import PersistException
from pycrawler.persist import MongoPersist
from pycrawler.persist import Item


class TestMongoPersist(TestCase):
    def test_setargs(self):
        p = MongoPersist(SpiderTest('testspider'))
        args = {'collection': 'testcoll'}
        p.setargs(args)
        self.assertEqual('testcoll', p.mongo.coll_name)

    def test_save(self):
        class Bean(Item):
            def __init__(self, _id, name, body):
                super(Bean, self).__init__()
                self._id = _id
                self.name = name
                self.body = body

            def persistable(self):
                d = {'_id': self._id,
                     'name': self.name,
                     'body': self.body}
                return d
        p = MongoPersist(SpiderTest('testspider'))
        self.assertRaises(PersistException, p.save, 'failed')
        self.assertRaises(PersistException, p.save, [1])
        before = p.mongo.count()
        p.save(Bean(1, 'test', 'case body'))
        after = p.mongo.count()
        self.assertEqual(1, after-before)
__author__ = 'mengpeng'
from unittest import TestCase
from test_scraper import SpiderTest
from pycrawler.exception import PersistException
from pycrawler.persist import MongoPersist
from mongojuice.document import Document


class TestMongoPersist(TestCase):
    def test_setargs(self):
        p = MongoPersist(SpiderTest('testspider'))
        args = {'collection': 'testcoll'}
        p.setargs(args)
        self.assertEqual('testcoll', p.mongo.collection.name)

    def test_save(self):
        class Bean(Document):
            structure = {'name': str,
                         'body': str}
            given = ['name', 'body']
            database = 'pycrawler'
            collection = 'testspider-items'

            def __init__(self, name, body):
                super(Bean, self).__init__()
                self.name = name
                self.body = body

        p = MongoPersist(SpiderTest('testspider'))
        self.assertRaises(PersistException, p.save, 'failed')
        self.assertRaises(PersistException, p.save, [1])
        before = p.mongo.count()
        p.save(Bean('test', 'case body'))
        after = p.mongo.count()
        self.assertEqual(1, after-before)
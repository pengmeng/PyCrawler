# -*- coding: utf-8 -*-
from unittest import TestCase
from pycrawler.frontier import Frontier
from pycrawler.exception import FrontierException
from test_scraper import SpiderTest


class TestBFSFrontier(TestCase):
    def test_add(self):
        f = Frontier.get('BFSFrontier')(SpiderTest('testspider'))
        urls = ['http://www.sample{0}.com'.format(x) for x in xrange(5)]
        f.clean('todo')
        f.add(urls[0])
        f.add(urls[1:], True)
        self.assertEqual(5, len(f))
        f.clean('visited')

    def test__addone(self):
        f = Frontier.get('BFSFrontier')(SpiderTest('testspider'))
        url = 'http://www.google.com'
        f.clean('todo')
        f._addone(url, False)
        self.assertEqual(1, len(f))

    def test_next(self):
        pass

    def test__nextone(self):
        f = Frontier.get('BFSFrontier')(SpiderTest('testspider'))
        f.clean('todo')
        f.add('url-for-test-nextone')
        self.assertEqual(1, len(f))
        item = f._nextone()
        self.assertIsInstance(item, str)
        self.assertEqual(1, f.filter.count)

    def test__nextall(self):
        f = Frontier.get('BFSFrontier')(SpiderTest('testspider'))
        f.clean('todo')
        f.add(['http://www.sample{0}.com'.format(x) for x in xrange(5)])
        items = f._nextall()
        self.assertEqual(5, len(items))
        f.clean('visited')

    def test_clean(self):
        f = Frontier.get('BFSFrontier')(SpiderTest('testspider'))
        f.clean('todo', 'visited')
        self.assertEqual(0, len(f))
        self.assertEqual(0, f.redis.llen(f.visited))
        f.add(['url1', 'url2'])
        self.assertEqual(2, len(f))
        f.next(0)
        self.assertEqual(2, f.redis.llen(f.visited))
        f.add('should left')
        f.clean('visited')
        self.assertEqual(0, f.redis.llen(f.visited))
        self.assertEqual(1, len(f))

    def test__feedfilter(self):
        f = Frontier.get('BFSFrontier')(SpiderTest('testspider'))
        f.clean('todo', 'visited')
        f.redis.rpush(f.visited, 'sample1')
        f.redis.rpush(f.visited, 'sample2')
        f.redis.rpush(f.visited, 'sample3')
        f._feedfilter()
        self.assertEqual(3, f.filter.count)
        f.clean('todo', 'visited')
        del f

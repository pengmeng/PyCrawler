__author__ = 'mengpeng'
from unittest import TestCase
from pycrawler.frontier import Frontier
from pycrawler.exception import FrontierException
from test_scraper import SpiderTest


class TestBFSFrontier(TestCase):
    def test_setargs(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
        args = {'rules': ['^http://', '[0-9]*']}
        f.setargs(args)
        self.assertEqual(2, len(f.args['rules']))
        args = {'rules': ['[0-9]', '[--']}
        self.assertRaises(FrontierException, f.setargs, args)

    def test_add(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
        urls = ['http://www.sample{0}.com'.format(x) for x in xrange(5)]
        f.add(urls[0])
        f.add(urls[1:])
        for each in urls:
            self.assertTrue(each in f)

    def test__addone(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
        url = 'http://www.google.com'
        f._addone(url)
        self.assertTrue(url in f)

    def test_next(self):
        pass

    def test__nextone(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
        before = len(f)
        if before == 0:
            f.add('url-for-test-nextone')
            before = 1
        item = f._nextone()
        after = len(f)
        self.assertIsInstance(item, str)
        self.assertEqual(1, f.filter.count)
        self.assertEqual(1, before-after)
        self.assertTrue(f.isVisited(item))

    def test__nextall(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
        before = f.filter.count
        items = f._nextall()
        after = f.filter.count
        self.assertEqual(0, len(f))
        self.assertEqual(len(items), after-before)
        if items:
            for each in items:
                self.assertTrue(f.isVisited(each))

    def test_validate(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
        args = {'rules': [
            '((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?']}
        f.setargs(args)
        self.assertTrue(f.validate('http://www.baidu.com'))

    def test_clean(self):
        f = Frontier.getFrontier('BFSFrontier')(SpiderTest('testspider'))
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
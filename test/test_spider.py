__author__ = 'mengpeng'
import time
from unittest import TestCase
from settings import SPIDER
from settings import DRIVER
from pycrawler.spider import Spider
from pycrawler.spider import Driver
from pycrawler.exception import PyCrawlerException


class TestSpider(TestCase):
    def test__build(self):
        sp = Spider(SPIDER)
        self.assertEqual('MySpider', sp.name)
        self.assertEqual(1, len(sp.handlers))
        del sp

    def test_addtask(self):
        sp = Spider(SPIDER)
        sp.frontier.clean('todo')
        sp.addtask('http://www.google.com')
        self.assertEqual(1, len(sp.frontier))
        sp.frontier.clean('todo')
        del sp

    def test_run(self):
        sp = Spider(SPIDER)
        sp.frontier.clean('todo', 'visited')
        url = ['http://www.google.com', 'http://www.baidu.com']
        sp.addtask(url)
        sp.run()
        self.assertEqual(0, len(sp.frontier))
        self.assertEqual(2, sp.frontier.redis.llen(sp.frontier.visited))
        sp.frontier.clean('todo', 'visited')
        self.assertTrue(sp.handlers[0]._exists(url[0]))
        self.assertTrue(sp.handlers[0]._exists(url[1]))
        del sp

    def test_retire(self):
        pass


class TestDriver(TestCase):
    def test__build(self):
        d = Driver(DRIVER)
        self.assertEqual(2, len(d))
        self.assertEqual('Spider1', d.getspider('Spider1').name)
        self.assertEqual('Spider2', d.getspider('Spider2').name)
        del d

    def test_addspider(self):
        d = Driver(DRIVER)
        self.assertRaises(PyCrawlerException, d.addspider, 'none')
        d.addspider(Spider(SPIDER))
        self.assertEqual(3, len(d))
        del d

    def test_getspider(self):
        d = Driver(DRIVER)
        self.assertIsInstance(d.getspider('Spider1'), Spider)
        self.assertRaises(PyCrawlerException, d.getspider, 'none')
        del d

    def test_addtask(self):
        d = Driver(DRIVER)
        s = d.getspider('Spider1')
        s.frontier.clean('todo', 'visited')
        before = len(s.frontier)
        d.addtask('Spider1', 'http://www.nevervisited.com')
        after = len(s.frontier)
        self.assertEqual(1, after-before)
        self.assertRaises(PyCrawlerException, d.addtask, 'none', 'none')
        s.frontier.clean('todo', 'visited')
        del d

    def test_start(self):
        d = Driver(DRIVER)
        d.getspider('Spider1').frontier.clean('todo', 'visited')
        d.getspider('Spider2').frontier.clean('todo', 'visited')
        urls = ['http://www.google.com', 'http://www.baidu.com', 'http://www.zhihu.com']
        d.addtask('Spider1', urls)
        d.addtask('Spider2', urls[0])
        d.start()
        d.pause()
        time.sleep(5)
        d.resume()
        time.sleep(5)
        d.stop()
        d.getspider('Spider1').frontier.clean('todo', 'visited')
        d.getspider('Spider2').frontier.clean('todo', 'visited')
__author__ = 'mengpeng'
from unittest import TestCase
from settings import SPIDER
from settings import DRIVER
from pycrawler.spider import Spider


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
        pass

    def test_addspider(self):
        pass

    def test_getspider(self):
        pass

    def test_addtask(self):
        pass

    def test_start(self):
        pass
# -*- coding: utf-8 -*-
from unittest import TestCase
from cookielib import CookieJar
from pycrawler.scraper import Scraper
from pycrawler.scraper import DefaultScraper
from pycrawler.scraper import DefaultCookieScraper
from pycrawler.scraper import encodeurl
from pycrawler.scraper import parseurl
from pycrawler.exception import ScraperException
from pycrawler.logger import Logger


class TestScraper(TestCase):
    def test_register(self):
        self.assertRaises(ScraperException, Scraper.register, 0)
        self.assertEqual(DefaultScraper, Scraper.Dict['DefaultScraper'])

    def test_getScraper(self):
        self.assertRaises(ScraperException, Scraper.get, 'None')
        self.assertEqual(DefaultScraper, Scraper.get('DefaultScraper'))
        self.assertIsInstance(Scraper.get('DefaultScraper')(SpiderTest('testspider')), DefaultScraper)


class TestDefaultScraper(TestCase):
    def test_fetchone(self):
        sp = SpiderTest('testspider')
        s = DefaultScraper(sp)
        _, html = s.fetchone('http://www.baidu.com')
        self.assertNotEqual(0, len(html))

    def test_fetch(self):
        sp = SpiderTest('testspider')
        s = DefaultScraper(sp)
        results = s.fetch(['http://www.renren.com',
                           'http://www.baidu.com',
                           'http://www.zhihu.com'])
        self.assertEqual(3, len(results))
        for value in results.itervalues():
            self.assertNotEqual(0, len(value))

    def test_url(self):
        url = 'http://www.google.com'
        data = {'a': 1, 'b': 2, 'c': 3}
        full = encodeurl('POST', url, data)
        self.assertTrue('<args>' in full)
        url2, data2 = parseurl(full)
        self.assertEqual(url, url2)
        self.assertEqual(data, data2)


class SpiderTest:
    def __init__(self, name):
        self.name = name
        self.logger = Logger('Default')
        self.scraper = DefaultScraper(self)

    def addtask(self, task):
        print('{0} got url(s):'.format(self.name))
        print(task)


class TestDefaultCookieScraper(TestCase):
    def test__check_opener(self):
        sp = SpiderTest('testspider')
        scraper = DefaultCookieScraper(sp)
        self.assertRaises(ScraperException, scraper._check_opener)
        scraper.setargs({'getCookie': 1})
        self.assertRaises(ScraperException, scraper._check_opener)
        scraper.setargs({'getCookie': lambda: 1})
        self.assertRaises(ScraperException, scraper._check_opener)
        scraper.setargs({'getCookie': lambda: CookieJar()})
        scraper._check_opener()
        self.assertIsNotNone(scraper.opener)

    def test_fetch(self):
        sp = SpiderTest('testspider')
        s = DefaultCookieScraper(sp)
        s.setargs({'getCookie': lambda: CookieJar()})
        results = s.fetch(['http://www.renren.com',
                           'http://www.baidu.com',
                           'http://www.zhihu.com'])
        self.assertEqual(3, len(results))
        for value in results.itervalues():
            self.assertNotEqual(0, len(value))

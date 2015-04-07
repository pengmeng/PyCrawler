__author__ = 'mengpeng'
from unittest import TestCase
from pycrawler.scraper import Scraper
from pycrawler.scraper import DefaultScraper
from pycrawler.exception import ScraperException


class TestScraper(TestCase):
    def test_register(self):
        self.assertRaises(ScraperException, Scraper.register, 0)
        self.assertEqual(DefaultScraper, Scraper.Dict['DefaultScraper'])

    def test_getScraper(self):
        self.assertRaises(ScraperException, Scraper.getScraper, 'None')
        self.assertEqual(DefaultScraper, Scraper.getScraper('DefaultScraper'))
        self.assertIsInstance(Scraper.getScraper('DefaultScraper')(''), DefaultScraper)


class TestDefaultScraper(TestCase):
    def test_fetchone(self):
        sp = SpiderTest('testspider')
        s = DefaultScraper(sp)
        _, html = s.fetchone('http://www.google.com')
        self.assertNotEqual(0, len(html))

    def test_fetch(self):
        sp = SpiderTest('testspider')
        s = DefaultScraper(sp)
        results = s.fetch(['http://www.google.com',
                           'http://www.baidu.com',
                           'http://www.zhihu.com'])
        self.assertEqual(3, len(results))
        for value in results.itervalues():
            self.assertNotEqual(0, len(value))

    def test_url(self):
        url = 'http://www.google.com'
        data = {'a': 1, 'b': 2, 'c': 3}
        full = DefaultScraper.encodeurl('POST', url, data)
        self.assertTrue('<args>' in full)
        url2, data2 = DefaultScraper.parseurl(full)
        self.assertEqual(url, url2)
        self.assertEqual(data, data2)


class SpiderTest:
    def __init__(self, name):
        self.name = name
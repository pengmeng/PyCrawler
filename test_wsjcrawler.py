__author__ = 'mengpeng'
import unittest
from unittest import TestCase
from test.test_scraper import SpiderTest
from WSJCrawler import *


class TestBasicFunc(TestCase):
    def test_lastday(self):
        self.assertEqual(31, lastday(2015, 1))
        self.assertEqual(29, lastday(2000, 2))
        self.assertEqual(30, lastday(2015, 4))

    def test_date2num(self):
        self.assertEqual(20150413, date2num('04/13/15'))

    def test_generateseeds(self):
        urls = generateseeds('seed1', [2015], [1, 2, 3, 4])
        self.assertEqual(4, len(urls))
        urls = generateseeds('seed2', [2014, 2015], [1, 2, 3, 10, 11, 12])
        self.assertEqual(12, len(urls))


class TestWSJHandler(TestCase):
    @unittest.skip('succ')
    def test_parse(self):
        h = WSJHandler(SpiderTest('testspider'))
        data = {'fromDate': '04/01/15', 'toDate': '04/30/15', 'page_no': ''}
        url = DefaultScraper.encodeurl('POST', 'http://online.wsj.com/search/term.html?KEYWORDS=deflation', data)
        with open('notfound.html') as f:
            html = f.read()
        self.assertIsNone(h.parse(html, url))
        with open('temp.html') as f:
            html = f.read()
        results = h.parse(html, url)
        self.assertEqual(16, len(results))
        phase = results[0]
        self.assertEqual(2, phase.pages)
        self.assertEqual(30, phase.total)
        self.assertEqual('deflation', phase.keyword)
        self.assertEqual(20150401, phase.start)
        self.assertEqual(20150430, phase.end)
        self.assertEqual(2015, phase.year)
        self.assertEqual(4, phase.month)

    def test__parsepage(self):
        h = WSJHandler(SpiderTest('testspider'))
        s1 = '<li class="listFirst"> 1-15 of 30</li>'
        s2 = '<li class="listFirst"> 16-30 of 30</li>'
        s3 = '<li class="listFirst"> 16-30 of 1,330</li>'
        data = {'fromDate': '04/01/15', 'toDate': '04/30/15', 'page_no': '', 'KEYWORDS': 'deflation'}
        url = DefaultScraper.encodeurl('POST', 'http://online.wsj.com/search/term.html?KEYWORDS=deflation', data)
        phase = h._parsepage(s1, url)
        self.assertEqual(2, phase.pages)
        self.assertEqual(30, phase.total)
        self.assertEqual('deflation', phase.keyword)
        self.assertEqual(20150401, phase.start)
        self.assertEqual(20150430, phase.end)
        self.assertEqual(2015, phase.year)
        self.assertEqual(4, phase.month)
        phase = h._parsepage(s2, url)
        self.assertIsNone(phase)
        phase = h._parsepage(s3, url)
        self.assertIsNone(phase)

    def test__parsekeyword(self):
        h = WSJHandler(SpiderTest('testspider'))
        data = {'fromDate': '04/01/15', 'toDate': '04/30/15', 'page_no': '', 'KEYWORDS': 'deflation'}
        url = DefaultScraper.encodeurl('POST', 'http://online.wsj.com/search/term.html?KEYWORDS=deflation', data)
        self.assertEqual('deflation', h._parsekeyword(url))

    def test__parsetitle(self):
        h = WSJHandler(SpiderTest('testspider'))
        s = '<a class="mjLinkItem " href="http://blogs.wsj.com/moneybeat/2015/04/13/have-central-banks-learned-to-distinguish-good-from-bad-deflation/?KEYWORDS=deflation">Have Central Banks Learned to Distinguish \xe2\x80\x98Good\xe2\x80\x99 From \xe2\x80\x98Bad\xe2\x80\x99 Deflation?</a>'
        href, title = h._parsetitle(s)
        print(href)
        print(title)

    def test__parsedate(self):
        h = WSJHandler(SpiderTest('testspider'))
        s = '<li class="metadataType-timeStamp first">04/05/15'
        self.assertEqual('04/05/15', h._parsedate(s))

    def test__parsetag(self):
        h = WSJHandler(SpiderTest('testspider'))
        s = '<li class="metadataType-section">MoneyBeat</li>'
        self.assertEqual('MoneyBeat', h._parsetag(s))
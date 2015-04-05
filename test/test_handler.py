__author__ = 'mengpeng'
import os
from unittest import TestCase
from pycrawler.handler import TempHandler
from pycrawler.utils.tools import gethash
from test_scraper import SpiderTest


class TestTempHandler(TestCase):
    def test_setargs(self):
        h = TempHandler(SpiderTest('testspider'))
        self.assertEqual('./tmp/testspider/', h.args['path'])
        args = {'path': './newpath/'}
        h.setargs(args)
        self.assertEqual('./newpath/testspider/', h.args['path'])

    def test_parse(self):
        h = TempHandler(SpiderTest('testspider'))
        h.parse('conent', 'testurl1')
        self.assertTrue(os.path.exists(h._tmpfilename('testurl1')))

    def test__tmpfilename(self):
        h = TempHandler(SpiderTest('testspider'))
        self.assertEqual('./tmp/testspider/'+str(gethash('sample'))+'.html', h._tmpfilename('sample'))
        self.assertTrue(os.path.exists('./tmp/'))
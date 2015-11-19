# -*- coding: utf-8 -*-
from __future__ import absolute_import
import ast
import urllib
import socket
from cookielib import CookieJar

import eventlet
from eventlet.green import urllib2
from pycrawler.exception import ScraperException


def parseurl(url):
    data = None
    if '<args>' in url:
        parts = url.split('<args>')
        if len(parts) != 2:
            raise ScraperException('Wrong post url format: ' + url)
        url = parts[0]
        try:
            data = ast.literal_eval(parts[1])
        except ValueError:
            raise ScraperException('Wrong post args format: ' + parts[1])
    return url, data


def encodeurl(method, url, data=None):
    if method == 'POST' and data:
        url += '<args>' + data.__str__()
        return url
    elif method == 'GET' and data:
        url += urllib.urlencode(data)
        return url
    elif not data:
        return url
    else:
        raise ScraperException('Unsupported http method: ' + method)


class Scraper(object):
    Dict = {}

    def __init__(self):
        self.logger = None
        self.opener = None
        self.name = None
        self.args = None
        self._spider = None
        self.error_handler = None

    @staticmethod
    def register(cls):
        if isinstance(cls, type):
            Scraper.Dict[cls.__name__] = cls
            return cls
        else:
            raise ScraperException('Must register scraper with class name')

    @staticmethod
    def get(name):
        if name in Scraper.Dict:
            return Scraper.Dict[name]
        else:
            raise ScraperException('No scraper class named ' + name)

    @staticmethod
    def _error_handler(spider, error_message, url):
        spider.logger.warning(spider.scraper.name, error_message + ': ' + url)

    def setargs(self, args):
        if not isinstance(args, dict):
            raise ScraperException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value
        if 'error_handler' in self.args:
            self.error_handler = self.args['error_handler']

    def fetchone(self, oriurl):
        url, data = parseurl(oriurl)
        data = urllib.urlencode(data) if data else data
        res_url, html = None, None
        try:
            res = self.opener.open(url, data, self.args['timeout'])
        except (urllib2.HTTPError, IOError, socket.timeout) as ex:
            message = ex.message if isinstance(ex, socket.timeout) else 'IOError'
            self.error_handler(self._spider, message, oriurl)
        else:
            html = res.read()
            res_url = res.url
            res.close()
            if self.args['debug']:
                self.logger.info(self.name, 'Scraped: ' + url)
        return res_url, html

    def fetch(self, urllist):
        results = {}
        pool = eventlet.GreenPool()
        for url, html in pool.imap(self.fetchone, urllist):
            if html:
                results[url] = html
        return results


@Scraper.register
class DefaultScraper(Scraper):
    def __init__(self, spider):
        super(DefaultScraper, self).__init__()
        self._spider = spider
        self.logger = spider.logger
        self.name = spider.name + '-Scraper'
        self.opener = urllib2.build_opener()
        self.args = {'debug': True,
                     'timeout': 10}
        self.error_handler = Scraper._error_handler


@Scraper.register
class DefaultCookieScraper(Scraper):
    def __init__(self, spider):
        super(DefaultCookieScraper, self).__init__()
        self._spider = spider
        self.logger = spider.logger
        self.name = spider.name + '-Scraper'
        self.args = {'debug': True,
                     'timeout': 10,
                     'getCookie': None}
        self.opener = None
        self.error_handler = Scraper._error_handler

    def _check_opener(self):
        if self.opener:
            return
        getCookie = self.args['getCookie']
        if not getCookie or not callable(getCookie):
            raise ScraperException('Must set getCookie function before running DefaultCookieScraper')
        cookie = getCookie()
        if not issubclass(cookie.__class__, CookieJar):
            raise ScraperException('getCookie function must return an instance of subclass of cookielib.CookieJar')
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

    def fetch(self, urllist):
        self._check_opener()
        return super(DefaultCookieScraper, self).fetch(urllist)

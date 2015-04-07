__author__ = 'mengpeng'
import eventlet
import ast
import urllib
from eventlet.green import urllib2
from pycrawler.utils.tools import fullstamp
from pycrawler.exception import ScraperException


class Scraper(object):
    Dict = {}

    def __init__(self, spider):
        pass

    @staticmethod
    def register(cls):
        if isinstance(cls, type):
            Scraper.Dict[cls.__name__] = cls
            return cls
        else:
            raise ScraperException('Must register scraper with class name')

    @staticmethod
    def getScraper(name):
        if name in Scraper.Dict:
            return Scraper.Dict[name]
        else:
            raise ScraperException('No scraper class named '+name)

    def setargs(self, args):
        raise NotImplementedError

    def fetch(self, *args):
        raise NotImplementedError


@Scraper.register
class DefaultScraper(Scraper):

    def __init__(self, spider):
        super(DefaultScraper, self).__init__(spider)
        self._spider = spider
        self.args = {'debug': True}

    def setargs(self, args):
        if not isinstance(args, dict):
            raise ScraperException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value

    def fetchone(self, url):
        try:
            url, data = self._parseurl(url)
            res = urllib2.urlopen(url=url, data=data)
            html = res.read()
            res.close()
            if self.args['debug']:
                print('{0} [{1}] Scraped: {2}'.format(fullstamp(), self._spider.name, url))
            return url, html
        except IOError as e:
            raise ScraperException(e.message)

    def fetch(self, urllist):
        results = {}
        pool = eventlet.GreenPool()
        for url, html in pool.imap(self.fetchone, urllist):
            results[url] = html
        return results

    def parseurl(self, url):
        data = None
        if '<args>' in url:
            parts = url.splits('<args>')
            if len(parts) != 2:
                raise ScraperException('Wrong post url format: '+url)
            url = parts[0]
            try:
                data = ast.literal_eval(parts[1])
            except ValueError:
                raise ScraperException('Wrong post args format: '+parts[1])
        return url, data

    def encodeurl(self, method, url, data=None):
        if method == 'POST' and data:
            url += '<args>' + data.__str__()
            return url
        elif method == 'GET' and data:
            url += urllib.urlencode(data)
            return url
        elif not data:
            return url
        else:
            raise ScraperException('Unsupported http method: '+method)
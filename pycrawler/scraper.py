__author__ = 'mengpeng'
import os
import eventlet
from eventlet.green import urllib2
from pycrawler.utils.tools import gethash
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

    def fetch(self, *args):
        raise ScraperException('Method must be override')


@Scraper.register
class DefaultScraper(Scraper):

    def __init__(self, spider):
        super(DefaultScraper, self).__init__(spider)
        self._spider = spider
        self.args = {'debug': True,
                     'tempFile': True,
                     'tempPath': './tmp/'}

    def fetchone(self, url):
        try:
            html = urllib2.urlopen(url)
            if self.args['debug']:
                print('{0} [{1}] Scraped: {2}'.format(fullstamp(), self._spider.name, url))
            return html
        except IOError as e:
            raise ScraperException(e.message)

    def fetch(self, urllist):
        results = {}
        pool = eventlet.GreenPool()
        for each in pool.imap(self.fetchone, urllist):
            results[gethash(each.geturl())] = each
        return results

    def _loadfile(self, url):
        filename = self._tmpfilename(url)
        with open(filename, 'r') as infile:
            content = infile.read()
        return content

    def _save2file(self, url, content):
        filename = self._tmpfilename(url)
        with open(filename, 'w') as outfile:
            outfile.write(content)
            outfile.flush()

    def _tmpfilename(self, url):
        if not os.path.exists(self.args['tempPath']):
            os.mkdir(self.args['tempPath'])
        return self.args['tempPath'] + str(gethash(url)) + '.html'
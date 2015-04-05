__author__ = 'mengpeng'
import os
import urllib
from pycrawler.utils.tools import gethash
from pycrawler.exception import ScraperException


class Scraper(object):
    Dict = {}

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


@Scraper.register
class DefaultScraper(object):

    def __init__(self, debug=False, spidermode=False, tmpfile=True):
        self.debug = debug
        self.spidermode = spidermode
        self.tmpfile = tmpfile

    def exists(self, url):
        filename = self._tmpfilename(url)
        return os.path.exists(filename)

    def fetchone(self, url, *handlers):
        result = self.fetch([url], *handlers)
        return result and result[gethash(url)]

    def fetch(self, urllist, *handlers):
        results = {}
        for url in iter(urllist):
            if self.exists(url):
                if not self.spidermode:
                    html = self._loadfile(url)
                    if self.debug:
                        print('Load {0}.html from file.'.format(gethash(url)))
                else:
                    if self.debug:
                        print('{0}.html already visited.'.format(gethash(url)))
                    continue
            else:
                html = self._download(url)
                if self.tmpfile:
                    self._save2file(url, html)
                    if self.debug:
                        print('Download {0} and save as {1}.html'.format(url, gethash(url)))
            result = []
            for handler in iter(handlers):
                result.append(handler.parse(html, url))
            results[gethash(url)] = result
        return results

    def _download(self, url):
        html = urllib.urlopen(url).read()
        return html

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
        if not os.path.exists('./tmp'):
            os.mkdir('./tmp')
        return './tmp/' + str(gethash(url)) + '.html'
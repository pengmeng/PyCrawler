__author__ = 'mengpeng'
import os
from bs4 import BeautifulSoup
from pycrawler.exception import HandlerException
from pycrawler.utils.tools import gethash


class Handler(object):
    Dict = {}

    def __init__(self, spider):
        pass

    @staticmethod
    def register(cls):
        if isinstance(cls, type):
            Handler.Dict[cls.__name__] = cls
            return cls
        else:
            raise HandlerException('Must register Handler with class name')

    @staticmethod
    def get(name):
        if name in Handler.Dict:
            return Handler.Dict[name]
        else:
            raise HandlerException('No Handler class named '+name)

    def setargs(self, args):
        raise NotImplementedError

    def parse(self, *args):
        raise NotImplementedError


@Handler.register
class TempHandler(Handler):
    def __init__(self, spider):
        super(TempHandler, self).__init__(spider)
        self._spider = spider
        self.args = {'path': './tmp/'+spider.name+'/',
                     'overwrite': True}

    def setargs(self, args):
        if not isinstance(args, dict):
            raise HandlerException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value
        if self.args['path'].endswith('/'):
            self.args['path'] += self._spider.name + '/'
        else:
            self.args['path'] += '/' + self._spider.name + '/'

    def parse(self, html, url):
        if self.args['overwrite']:
            self._save2file(url, html)
        elif not self._exists(url):
            self._save2file(url, html)

    def _exists(self, url):
        filename = self._tmpfilename(url)
        return os.path.exists(filename)

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
        if not os.path.exists(self.args['path']):
            os.makedirs(self.args['path'])
        return self.args['path'] + str(gethash(url)) + '.html'


@Handler.register
class LinkHandler(Handler):

    def __init__(self, spider):
        super(LinkHandler, self).__init__(spider)
        self.spider = spider

    def setargs(self, args):
        pass

    def parse(self, html, url):
        bs = BeautifulSoup(html)
        result = []
        for link in bs.find_all('a', href=True):
            href = link.get('href')
            if href and self._satisfy(href):
                result.append(str(href))
        result = list(set(result))
        self.spider.addtask(result)

    def _satisfy(self, href):
        return href.startswith('http://')
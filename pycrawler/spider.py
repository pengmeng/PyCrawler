__author__ = 'mengpeng'
import os
from threading import Thread
from pycrawler.exception import PyCrawlerException
from pycrawler.scraper import Scraper
from pycrawler.frontier import Frontier
from pycrawler.handler import Handler
from pycrawler.persist import Persist
from pycrawler.utils.tools import fullstamp


class Spider(Thread):
    def __init__(self, config, debug=True):
        super(Spider, self).__init__()
        self.name = ''
        self.config = config
        self.scraper = None
        self.frontier = None
        self.handlers = []
        self.persist = None
        self.debug = debug
        self._build(config)
        self.keep = True
        self.pause = False

    def _build(self, config):
        try:
            self.name = config['name']
            self.debug = config.get('debug', True)
            self._debug('Start building...')
            self.scraper = Scraper.getScraper(config['scraper']['name'])(self)
            if 'args' in config['scraper']:
                self.scraper.setargs(config['scraper']['args'])
            self.frontier = Frontier.getFrontier(config['frontier']['name'])(self)
            if 'args' in config['frontier']:
                self.frontier.setargs(config['frontier']['args'])
            for each in config['handlers']:
                handler = Handler.getHandler(each['name'])(self)
                if 'args' in each:
                    handler.setargs(each['args'])
                self.handlers.append(handler)
            self.persist = Persist.getPersist(config['persist']['name'])(self)
            if 'args' in config['persist']:
                self.persist.setargs(config['persist']['args'])
            self._debug('Build successful!')
        except KeyError as e:
            raise PyCrawlerException('Key \''+e.args[0]+'\' missing in config dict')

    def reload(self, config):
        self._build(config)

    def addtask(self, task):
        self.frontier.add(task)

    def run(self):
        self._debug('Start crawling...')
        while self.frontier.hasnext() and self.keep:
            urls = self.frontier.next(100)
            results = self.scraper.fetch(urls)
            for url, body in results.iteritems():
                for handler in self.handlers:
                    item = handler.parse(body, url)
                    if item:
                        self.persist.save(item)
            self._pause()
        self._debug('Crawling finished!')

    def retire(self):
        self.pause = False
        self.keep = False
        self._debug('Stopped by driver')
        #self.frontier.save()

    def recover(self, filename):
        if not os.path.exists(filename):
            self._debug('File {0} not found'.format(filename))
        else:
            self._debug('Recovering from '+filename)
            count = 0
            with open(filename, 'r') as f:
                for each in f.readlines():
                    count += 1
                    url, body = self.scraper.fetchone(each)
                    for handler in self.handlers:
                        item = handler.parse(body, url)
                        if item:
                            self.persist.save(item)
            self._debug('Recovered {0} urls'.format(count))

    def clean(self, *args):
        self.frontier.clean(*args)

    def report(self):
        print(self.name+' report:')
        print('Todo urls: {0}'.format(len(self.frontier)))
        print('Visited urls: {0}'.format(self.frontier.visitednum()))
        print('Failed urls: {0}'.format('Not supported'))
        print('Saved items: {0}'.format(len(self.persist)))

    def _pause(self):
        if self.pause:
            self._debug('Paused by driver')
            while True:
                if not self.pause:
                    self._debug('Resume...')
                    break

    def _debug(self, s):
        if self.debug:
            print('{0} [{1}] {2}'.format(fullstamp(), self.name, s))


class Driver(object):
    def __init__(self, config, debug=True):
        self.name = ''
        self.config = config
        self.spiders = {}
        self.debug = debug
        self._build(config)

    def __len__(self):
        return len(self.spiders)

    def _build(self, config):
        try:
            self.name = config['name']
            self.debug = config.get('debug', True)
            self._debug('Start building...')
            for each in config['spiders']:
                spider = Spider(each)
                self.addspider(spider)
            self._debug('Build successful!')
        except KeyError as e:
            raise PyCrawlerException('Key \''+e.args[0]+'\' missing in config dict')

    def addspider(self, spider):
        if isinstance(spider, Spider):
            self.spiders[spider.name] = spider
        else:
            raise PyCrawlerException('Only accept object of Spider')

    def getspider(self, name):
        try:
            spider = self.spiders[name]
            return spider
        except KeyError:
            raise PyCrawlerException('No spider named \''+name+'\'')

    def addtask(self, spidername, task):
        spider = self.getspider(spidername)
        spider.addtask(task)

    def start(self):
        self._debug('Start spiders...')
        for spider in self.spiders.itervalues():
            spider.start()

    def pause(self):
        for spider in self.spiders.itervalues():
            if spider.isAlive():
                spider.pause = True

    def resume(self):
        for spider in self.spiders.itervalues():
            if spider.isAlive():
                spider.pause = False

    def stop(self):
        self._debug('Stop spiders...')
        for spider in self.spiders.itervalues():
            if spider.isAlive():
                spider.retire()
        self._debug('Shut down.')

    def recover(self, spidername, filename):
        spider = self.getspider(spidername)
        self._debug('Recover {0} from {1}'.format(spidername, filename))
        spider.recover(filename)
        spider.clean('todo')
        spider.report()

    def report(self):
        print(self.name+' report:\n')
        for spider in self.spiders.itervalues():
            spider.report()
            print('')

    def _debug(self, s):
        if self.debug:
            print('{0} [{1}] {2}'.format(fullstamp(), self.name, s))
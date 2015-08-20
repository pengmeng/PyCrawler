# -*- coding: utf-8 -*-
__author__ = 'mengpeng'
from threading import Thread

from mongojuice.document import Document

import os
from pycrawler.exception import PyCrawlerException
from pycrawler.scraper import Scraper
from pycrawler.frontier import Frontier
from pycrawler.handler import Handler
from pycrawler.logger import Logger
from pycrawler.utils.tools import fullstamp


class Spider(Thread):
    def __init__(self, config, debug=True):
        super(Spider, self).__init__()
        self.name = ''
        self.config = config
        self.scraper = None
        self.frontier = None
        self.handlers = []
        self.logger = None
        self.debug = debug
        self._build(config)
        self.keep = True
        self.ispaused = False

    def _build(self, config):
        try:
            self.name = config['name']
            Logger.register(self.name)
            Logger.load()
            self.logger = Logger(self.name)
            self.debug = config.get('debug', True)
            self.logger.info(self.name, 'Start building...')
            self.scraper = Scraper.get(config['scraper']['name'])(self)
            if 'args' in config['scraper']:
                self.scraper.setargs(config['scraper']['args'])
            self.frontier = Frontier.get(config['frontier']['name'])(self)
            if 'args' in config['frontier']:
                self.frontier.setargs(config['frontier']['args'])
            for each in config['handlers']:
                handler = Handler.get(each['name'])(self)
                if 'args' in each:
                    handler.setargs(each['args'])
                self.handlers.append(handler)
            self.logger.info(self.name, 'Build successful!')
        except KeyError as e:
            raise PyCrawlerException('Key \'' + e.args[0] + '\' missing in config dict')

    def reload(self, config):
        self._build(config)

    def addtask(self, task):
        self.frontier.add(task)

    def run(self):
        self.logger.warning(self.name, 'Start crawling...')
        while self.frontier.hasnext() and self.keep:
            urls = self.frontier.next(100)
            results = self.scraper.fetch(urls)
            for url, body in results.iteritems():
                for handler in self.handlers:
                    items = handler.parse(body, url)
                    if isinstance(items, list):
                        for item in items:
                            item.save()
                    elif isinstance(items, Document):
                        items.save()
            self._checkpause()
        self.logger.warning(self.name, 'Crawling finished!')

    def recover(self, filename):
        if not os.path.exists(filename):
            self.logger.info(self.name, 'File {0} not found'.format(filename))
        else:
            self.logger.info(self.name, 'Recovering from ' + filename)
            count = 0
            with open(filename, 'r') as f:
                for each in f.readlines():
                    url, body = self.scraper.fetchone(each)
                    if not body:
                        continue
                    count += 1
                    for handler in self.handlers:
                        items = handler.parse(body, url)
                        try:
                            if isinstance(items, list):
                                for item in items:
                                    item.save()
                            elif isinstance(items, Document):
                                items.save()
                        except AttributeError:
                            raise PyCrawlerException('Items must implement save() method.')
            self.logger.info(self.name, 'Recovered {0} urls'.format(count))

    def clean(self, *args):
        self.frontier.clean(*args)

    def report(self):
        s = self.summary()
        results = [self.name + ' report:',
                   'Todo urls: {0}'.format(s['todo']),
                   'Visited urls: {0}'.format(s['visited']),
                   'Failed urls: {0}'.format(s['failed'])]
        for each in results:
            print(each)

    def summary(self):
        result = {'todo': len(self.frontier),
                  'visited': self.frontier.visitednum(),
                  'failed': 'Not supported'}
        return result

    def pause(self):
        if self.isAlive() and not self.ispaused:
            self.ispaused = True

    def resume(self):
        if self.isAlive() and self.ispaused:
            self.ispaused = False

    def retire(self):
        if self.isAlive():
            self.logger.info(self.name, 'Stopped by driver')
            self.ispaused = False
            self.keep = False

    def _checkpause(self):
        if self.ispaused:
            self.logger.info(self.name, 'Paused by driver')
            while self.ispaused:
                pass
            else:
                self.logger.info(self.name, 'Resumed by driver')


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
            raise PyCrawlerException('Key \'' + e.args[0] + '\' missing in config dict')

    def addspider(self, spider):
        if isinstance(spider, Spider):
            self.spiders[spider.name] = spider
        else:
            raise PyCrawlerException('Only accept object of Spider')

    def getspider(self, name):
        return self.spiders.get(name)

    def getspiders(self):
        return self.spiders.itervalues()

    def addtask(self, spidername, task):
        spider = self.getspider(spidername)
        if spider:
            spider.addtask(task)
        else:
            raise PyCrawlerException('No spider named ' + spidername)

    def start(self):
        self._debug('Starting...')
        map(lambda s: s.start(), self.getspiders())

    def pause(self):
        map(lambda s: s.pause(), self.getspiders())

    def resume(self):
        map(lambda s: s.resume(), self.getspiders())

    def stop(self):
        map(lambda s: s.retire(), self.getspiders())
        self._debug('Shut down.')

    def recover(self, spidername, filename):
        spider = self.getspider(spidername)
        self._debug('Recover {0} from {1}'.format(spidername, filename))
        spider.recover(filename)
        spider.report()

    def report(self):
        print(self.name + ' report:\n')
        for spider in self.spiders.itervalues():
            spider.report()
            print('')

    def _debug(self, s):
        if self.debug:
            print('{0} [{1}] {2}'.format(fullstamp(), self.name, s))

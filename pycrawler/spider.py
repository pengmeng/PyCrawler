__author__ = 'mengpeng'
from threading import Thread
from pycrawler.exception import PyCrawlerException
from pycrawler.scraper import Scraper
from pycrawler.frontier import Frontier
from pycrawler.handler import Handler
from pycrawler.persist import Persist


class Spider(Thread):
    def __init__(self, config):
        super(Spider, self).__init__()
        self.name = ''
        self.config = config
        self.scraper = None
        self.frontier = None
        self.handlers = []
        self.persist = None
        self._build(config)

    def _build(self, config):
        try:
            self.name = config['name']
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
        except KeyError as e:
            raise PyCrawlerException('Key \''+e.args[0]+'\' missing in config dict')

    def reload(self, config):
        self._build(config)

    def addtask(self, task):
        self.frontier.add(task)

    def run(self):
        pass


class Driver(object):
    def __init__(self, config):
        self.name = ''
        self.config = config
        self.spiders = []

    def _build(self, config):
        pass

    def addspider(self, spider):
        if isinstance(spider, Spider):
            self.spiders.append(spider)
        else:
            raise PyCrawlerException('Only accept object of Spider')

    def start(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def stop(self):
        pass
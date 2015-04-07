__author__ = 'mengpeng'

#Example settings for building a single spider
#If don't use 'args', default args will be used.
SPIDER = {'name': 'MySpider',
          'debug': True,
          'scraper': {'name': 'DefaultScraper',
                      'args': {'debug': True}},
          'frontier': {'name': 'BFSFrontier',
                       'args': {'rules': ['((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?']}},
          'handlers': [{'name': 'TempHandler',
                        'args': {'path': './tmp/', 'overwrite': True}}],
          'persist': {'name': 'MongoPersist',
                      'args': {'db': 'pycrawler', 'collection': 'MySpider-items'}}}

#Example settings for building a driver with several spiders
DRIVER = {'name': 'MyCrawler',
          'debug': True,
          'spiders': [
              {'name': 'Spider1',
               'debug': True,
               'scraper': {'name': 'DefaultScraper',
                           'args': {'debug': True}},
               'frontier': {'name': 'BFSFrontier',
                            'args': {'rules': ['((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?']}},
               'handlers': [{'name': 'TempHandler',
                             'args': {'path': './tmp/', 'overwrite': True}}],
               'persist': {'name': 'MongoPersist',
                           'args': {'db': 'pycrawler', 'collection': 'MySpider-items'}}},
              {'name': 'Spider2',
               'scraper': {'name': 'DefaultScraper'},
               'frontier': {'name': 'BFSFrontier',
                            'args': {'rules': ['((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?']}},
               'handlers': [
                   {'name': 'TempHandler'},
                   {'name': 'LinkHandler'}],
               'persist': {'name': 'MongoPersist'}}
          ]}
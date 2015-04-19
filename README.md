PyCrawler
=====================
   [![Build Status](https://travis-ci.org/pengmeng/PyCrawler.svg?branch=master)](https://travis-ci.org/pengmeng/PyCrawler)  
A lightweight Python crawler framework

Requirements
---------------------
 - Python 2.7
 - MongoDB 3.0.1 for item storage
 - Redis 2.8.19 for default frontier implementation
 - Works on Mac OSX, Linux

Get Started
---------------------
### Services
``` shell
> mongod
> redis-server
```

### Install
``` shell
> pip install -r requirement.txt
```

### Create a crawler
The easist way to create a crawler is using a configuration dictionary.
``` python
DRIVER = {'name': 'FirstCrawler',
          'spiders': [
              {'name': 'Spider',
               'scraper': {'name': 'DefaultScraper'},
               'frontier': {'name': 'BFSFrontier'},
               'handlers': [
                   {'name': 'TempHandler'},
                   {'name': 'LinkHandler'}
               ],
               'persist': {'name': 'MongoPersist'}}
          ]}
```
This dictionary create a driver with one spider and using default arguments.
Then build and run this driver by:
``` python
import time
from pycrawler.spider import Driver

driver = Driver(DRIVER)
driver.addtask('Spider', 'http://www.google.com')
driver.start()
time.sleep(2)
driver.stop()
```
You will get output like this:
``` shell
```

### Demo (Customize)
WSJCrawler.py is a demo project for wall street journal website crawling. You can add customized scraper, handler or other class by decorator provided in related super class. Another important concept is item. You can create new item by extending super class Item. All these features can be found in the demo.

Thanks
---------------------
 - beautifulsoup4
 - eventlet
 - pybloom

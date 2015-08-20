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
> git clone git@github.com:pengmeng/PyCrawler.git
> cd PyCrawler
> git clone https://github.com/pengmeng/mongojuice.git
> pip install ./mongojuice/
> pip install -r requirement.txt
> pip install .
```

### Create a crawler
The easiest way to create a crawler is using a configuration dictionary.

``` python
DRIVER = {'name': 'FirstCrawler',
          'spiders': [
              {'name': 'Spider',
               'scraper': {'name': 'DefaultScraper'},
               'frontier': {'name': 'BFSFrontier'},
               'handlers': [
                   {'name': 'TempHandler'},
                   {'name': 'LinkHandler'}]}]}
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

```
2015-04-24 20:41:23 [FirstCrawler] Start building...
2015-04-24 20:41:23 [Spider] Start building...
2015-04-24 20:41:23 [Spider] Build successful!
2015-04-24 20:41:23 [FirstCrawler] Build successful!
2015-04-24 20:41:23 [FirstCrawler] Start spiders...
2015-04-24 20:41:23 [Spider] Start crawling...
2015-04-24 20:41:23 [Spider] Scraped: http://www.google.com
2015-04-24 20:41:23 [Spider] Scraped: http://www.google.com/imghp?hl=en&tab=wi
2015-04-24 20:41:24 [Spider] Scraped: http://www.google.com/intl/en/options/
2015-04-24 20:41:24 [Spider] Scraped: http://www.google.com/history/optout?hl=en
2015-04-24 20:41:24 [Spider] Scraped: http://maps.google.com/maps?hl=en&tab=wl
2015-04-24 20:41:24 [Spider] Scraped: http://www.youtube.com/?tab=w1
2015-04-24 20:41:24 [Spider] Scraped: http://news.google.com/nwshp?hl=en&tab=wn
2015-04-24 20:41:25 [FirstCrawler] Stop spiders...
2015-04-24 20:41:25 [Spider] Stopped by driver
2015-04-24 20:41:25 [FirstCrawler] Shut down.
2015-04-24 20:41:30 [Spider] Scraped: http://www.aysor.am/en/news/2015/04/24/Delegation-led-by-French-President-arrives-in-Yerevan/940680
...
2015-04-24 20:41:34 [Spider] Scraped: http://www.nytimes.com/aponline/2015/04/24/world/asia/ap-as-philippines-china.html
2015-04-24 20:41:40 [Spider] Crawling finished!
```

### Demo (Customize)
Coming soon...

Thanks
---------------------
 - beautifulsoup4
 - eventlet
 - pybloom
 - pymongo
 - redis (redis-py)
 - Unidecode

ToDo
---------------------
 - [ ] RediSugar - A redis-py wrapper
 - [ ] Refactor frontier.py
 - [ ] Refactor to Python 3.x
 - [x] Notification
 - [ ] Extract configuration
 - [ ] Add html parser template

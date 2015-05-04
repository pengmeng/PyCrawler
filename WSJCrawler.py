__author__ = 'mengpeng'
import sys
import re
import time
import math
import urllib
from unidecode import unidecode
from pycrawler.persist import Item
from pycrawler.handler import Handler
from pycrawler.scraper import DefaultScraper
from pycrawler.utils.tools import gethash
from pycrawler.utils.tools import fullstamp
from pycrawler.spider import Driver

SETTINGS = {'name': 'WSJCrawler',
            'spiders': [
                {'name': 'IncSpider',
                 'scraper': {'name': 'DefaultScraper'},
                 'frontier': {'name': 'BFSFrontier'},
                 'handlers': [{'name': 'WSJHandler'}],
                 'persist': {'name': 'MongoPersist',
                             'args': {'collection': 'wsj'}}},
                {'name': 'WordSpider',
                 'scraper': {'name': 'DefaultScraper'},
                 'frontier': {'name': 'BFSFrontier'},
                 'handlers': [{'name': 'WSJHandler'}],
                 'persist': {'name': 'MongoPersist',
                             'args': {'collection': 'wsj'}}}]}


def loadkeywords(filename):
    result = []
    with open(filename, 'r') as f:
        for word in f.readlines():
            word = word.strip()
            result.append(word)
    return result


def lastday(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        if (year % 100 != 0 and year % 4 == 0) or year % 400 == 0:
            return 29
        else:
            return 28


def date2num(date):
    """Parse date format 01/17/14 into int 20140117"""
    parts = date.split('/')
    if len(parts) != 3:
        parts = time.strftime("%m/%d/%y", time.localtime()).split('/')
    return ((2000 + int(parts[2])) * 100 + int(parts[0])) * 100 + int(parts[1])


class Phase(Item):
    def __init__(self, start, end, keyword, total):
        super(Phase, self).__init__()
        self.keyword = keyword
        self.total = total
        self.pages = int(math.ceil(float(total)/15))
        self.start = date2num(start)
        self.end = date2num(end)
        self.year = self.start / 10000
        self.month = self.start % 10000 / 100
        self._id = gethash(str(self.year) + str(self.month) + str(keyword))

    def persistable(self):
        result = {'_id': self._id,
                  'year': self.year,
                  'month': self.month,
                  'keyword': self.keyword,
                  'total': self.total,
                  'pages': self.pages,
                  'start': self.start,
                  'end': self.end}
        return result


class Article(Item):
    def __init__(self, title, url, date, tag, keyword):
        super(Article, self).__init__()
        self._id = gethash(title + date + keyword)
        self.title = title
        self.url = url
        self.date = self._cleandate(date)
        self.datenum = date2num(date)
        self.tag = tag
        self.keyword = keyword

    def _cleandate(self, date):
        if date.count('/') == 2:
            return date
        else:
            return time.strftime("%m/%d/%y", time.localtime())

    def persistable(self):
        result = {'_id': self._id,
                  'title': self.title,
                  'url': self.url,
                  'date': self.date,
                  'datenum': self.datenum,
                  'tag': self.tag,
                  'keyword': self.keyword}
        return result


@Handler.register
class WSJHandler(Handler):
    def __init__(self, spider):
        super(WSJHandler, self).__init__(spider)
        self._spider = spider
        self.logger = spider.logger
        self.name = spider.name+'-Handler'
        self.args = {'debug': True,
                     'log': True,
                     'logfile': 'WSJHandler.log'}

    def setargs(self, args):
        for key, value in args.iteritems():
            self.args[key] = value

    def parse(self, html, url):
        notfound = 'class="src_no_results"'
        if notfound in html:
            self.logger.warning(self.name, 'No results in '+url)
            return None
        pagep = re.compile('<li class="listFirst">[0-9of,\-\s]*</li>')
        titlep = re.compile('<a class="mjLinkItem.*</a>')
        tagp = re.compile('<li class="metadataType-section.*</li>')
        datep = re.compile('<li class="metadataType-timeStamp first">[0-9/]*')
        page = pagep.findall(html)
        if len(page) != 1:
            self.logger.error(self.name, 'Page index not found in '+url)
            return None
        titles = titlep.findall(html)
        dates = datep.findall(html)
        tags = tagp.findall(html)
        if len(titles) != len(tags):
            tags = ['']*len(titles)
        if len(titles) == len(dates) == len(tags):
            phase = self._parsepage(page[0], url)
            result = [phase] if phase else []
            keyword = self._parsekeyword(url)
            for i in xrange(len(titles)):
                href, title = self._parsetitle(titles[i])
                date = self._parsedate(dates[i])
                tag = self._parsetag(tags[i])
                article = Article(title, href, date, tag, keyword)
                result.append(article)
            return result
        else:
            self.logger.error(self.name, 'Item numbers not match in '+url)
            return None

    def _parsepage(self, page, oriurl):
        page = page[page.index('> ')+2:-5].strip()
        if ',' in page:
            page = page.replace(',', '')
        if page.startswith('1-'):
            url, data = DefaultScraper.parseurl(oriurl)
            keyword = url[url.index('=')+1:]
            total = int(page.split(' of ')[1])
            phase = Phase(data['fromDate'], data['toDate'], keyword, total)
            urls = []
            for i in xrange(2, phase.pages+1):
                data['page_no'] = i
                urls.append(DefaultScraper.encodeurl('POST', url, data))
            self._spider.addtask(urls)
            return phase

    def _parsekeyword(self, oriurl):
        _, data = DefaultScraper.parseurl(oriurl)
        return data['KEYWORDS']

    def _parsetitle(self, ori):
        href = ori[ori.index('href="')+6:ori.index('">')]
        title = ori[ori.index('">')+2:-4]
        title = unidecode(title.decode('utf-8'))
        return href, title

    def _parsedate(self, ori):
        return ori[-8:]

    def _parsetag(self, ori):
        return ori[ori.index('">')+2:-5] if ori != '' else ori


def main(option, *args):
    if option not in ['start', 'report', 'extract', 'recover']:
        print('Option not supported.')
        return
    if option == 'extract':
        if len(args) != 2:
            print('Usage: python WSJCrawler.py extract logfile outfile')
        else:
            extractlog(args[0], args[1])
        return
    driver = Driver(SETTINGS)
    if option == 'start':
        inckey = loadkeywords('inc.txt')
        url1, url2 = [], []
        years = list(range(2005, 2015))
        for each in iter(inckey):
            url1.extend(generateseeds(each, years))
            url1.extend(generateseeds(each, [2015], [1, 2, 3, 4]))
        wordkey = loadkeywords('word.txt')
        for each in iter(wordkey):
            url2.extend(generateseeds(each, years))
            url2.extend(generateseeds(each, [2015], [1, 2, 3, 4]))
        driver.addtask('IncSpider', url1)
        driver.addtask('WordSpider', url2)
        driver.start()
    elif option == 'report':
        driver.report()
    elif option == 'recover':
        if len(args) != 2:
            print('Usage: python WSJCrawler.py recover spidername urlfile')
        else:
            driver.recover(args[0], args[1])


def generateseeds(keyword, year, month=None):
    base = 'http://online.wsj.com/search/term.html?KEYWORDS=' + urllib.quote(keyword)
    data = {'KEYWORDS': keyword,
            'fromDate': '',
            'toDate': '',
            'source': 'WSJ.com',
            'media': 'All',
            'page_no': '',
            'sorted_by': 'relevance',
            'date_range': '90 days',
            'adv_search': 'open'}
    urls = []
    if not month:
        month = list(xrange(1, 13))
    for y in year:
        for m in month:
            ys = str(y % 100) if y % 100 >= 10 else ('0' + str(y % 100))
            ms = str(m) if m >= 10 else ('0' + str(m))
            d = lastday(y, m)
            ds = str(d) if d >= 10 else ('0' + str(d))
            data['fromDate'] = ms+'/01/'+ys
            data['toDate'] = ms+'/'+ds+'/'+ys
            urls.append(DefaultScraper.encodeurl('POST', base, data))
    return urls


def extractlog(logfile, outfile):
    print('Extracting urls from '+logfile)
    with open(outfile, 'w') as outf:
        with open(logfile, 'r') as inf:
            for each in inf.readlines():
                if 'No results' not in each and 'http://' in each:
                    each = each[each.index('http://'):]
                    outf.write(each)
        outf.flush()
    print('Done')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('   start:\t python WSJCrawler.py start')
        print('   report:\t python WSJCrawler.py report')
        print('   extract:\t python WSJCrawler.py extract logfile outfile')
        print('   recover:\t python WSJCrawler.py recover spidername urlfile')
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main(sys.argv[1], *sys.argv[2:])
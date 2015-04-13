__author__ = 'mengpeng'
import re
import time
import math
from unidecode import unidecode
from pycrawler.persist import Item
from pycrawler.handler import Handler
from pycrawler.scraper import DefaultScraper
from pycrawler.utils.tools import gethash
from pycrawler.utils.tools import fullstamp
from pycrawler.spider import Driver

SETTINGS = {'name': 'WSJCrawler',
            'spiders': [
                {'name': 'WSJSpider',
                 'scraper': {'name': 'DefaultScraper'},
                 'frontier': {'name': 'BFSFrontier'},
                 'handlers': [{'name': 'TempHandler',
                               'args': {'path': './tmp/'}},
                              {'name': 'WSJHandler'}],
                 'persist': {'name': 'MongoPersist',
                             'args': {'collection': 'wsj'}}}]}


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
        self._id = gethash(title + date)
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
        self.args = {'debug': True}

    def setargs(self, args):
        for key, value in args.iteritems():
            self.args[key] = value

    def parse(self, html, url):
        notfound = 'class="src_no_results"'
        if notfound in html:
            self._debug('No results in '+url)
            return None
        pagep = re.compile('<li class="listFirst">[0-9of\-\s]*</li>')
        titlep = re.compile('<a class="mjLinkItem.*</a>')
        tagp = re.compile('<li class="metadataType-section.*</li>')
        datep = re.compile('<li class="metadataType-timeStamp first">[0-9/]*')
        page = pagep.findall(html)
        if len(page) != 1:
            self._debug('Page index not found in '+url)
            return None
        titles = titlep.findall(html)
        dates = datep.findall(html)
        tags = tagp.findall(html)
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
            self._debug('Item numbers not match in '+url)
            return None

    def _parsepage(self, page, oriurl):
        page = page[page.index('> ')+2:-5].strip()
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
        url, _ = DefaultScraper.parseurl(oriurl)
        return url[url.index('=')+1:]

    def _parsetitle(self, ori):
        href = ori[ori.index('href="')+6:ori.index('">')]
        title = ori[ori.index('">')+2:-4]
        title = unidecode(title.decode('utf-8'))
        return href, title

    def _parsedate(self, ori):
        return ori[-8:]

    def _parsetag(self, ori):
        return ori[ori.index('">')+2:-5]

    def _debug(self, s, log=True):
        message = '{0} [{1}] {2}'.format(fullstamp(), WSJHandler.__name__, s)
        if self.args['debug']:
            print(message)
            if log:
                with open('WSJHandler.log', 'a') as f:
                    f.write(message+'\n')


def main():
    driver = Driver(SETTINGS)
    urls = generateseeds('deflation', [2015], [1, 2, 3])
    driver.addtask('WSJSpider', urls)
    driver.start()


def generateseeds(keyword, year, month):
    base = 'http://online.wsj.com/search/term.html?KEYWORDS=' + keyword
    data = {'KEYWORDS': keyword,
            'fromDate': '04/01/15',
            'toDate': '04/30/15',
            'source': 'WSJ.com',
            'media': 'All',
            'page_no': '',
            'sorted_by': 'relevance',
            'date_range': '90 days',
            'adv_search': 'open'}
    urls = []
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


if __name__ == '__main__':
    main()
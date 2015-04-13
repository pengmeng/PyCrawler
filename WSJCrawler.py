__author__ = 'mengpeng'
import re
from pycrawler.persist import Item
from pycrawler.handler import Handler
from pycrawler.scraper import DefaultScraper
from pycrawler.utils.tools import gethash
from pycrawler.utils.tools import fullstamp
SETTINGS = {'name': 'WSJCrawler',
            'spiders': [
                {'name': 'spider1',
                 'scraper': {'name': 'DefaultScraper'},
                 'frontier': {'name': 'BFSFrontier',
                              'args': {'rules': ['((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?']}},
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
        return 0
    else:
        return ((2000 + int(parts[2])) * 100 + int(parts[0])) * 100 + int(parts[1])


class Phase(Item):
    def __init__(self, start, end, keyword, total):
        super(Phase, self).__init__()
        self.keyword = keyword
        self.total = total
        self.pages = total / 15
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
        self.date = date
        self.datenum = date2num(date)
        self.tag = tag
        self.keyword = keyword

    def persistable(self):
        result = {'_id': self._id,
                  'title': self.title,
                  'url': self.url,
                  'date': self.date,
                  'datenum': self.datenum,
                  'tag': self.tag}
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
            for i in range(len(titles)):
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
            for i in range(2, phase.pages+1):
                data['page_no'] = i
                urls.append(DefaultScraper.encodeurl(url, data))
            self._spider.addtask(urls)
            return phase

    def _parsekeyword(self, oriurl):
        url, _ = DefaultScraper.parseurl(oriurl)
        return url[url.index('=')+1:]

    def _parsetitle(self, ori):
        href = ori[ori.index('href="')+6:ori.index('">')]
        title = ori[ori.index('">')+2:-4]
        return href, title

    def _parsedate(self, ori):
        return ori[-8:]

    def _parsetag(self, ori):
        return ori[ori.index('">')+2:-5]

    def _debug(self, s, log=True):
        message = '{0} [{1}] {2}\n'.format(fullstamp(), WSJHandler.__name__, s)
        if self.args['debug']:
            print(message)
            if log:
                with open('WSJHandler.log', 'a') as log:
                    log.write(message)


def main():
    pass

if __name__ == '__main__':
    pass
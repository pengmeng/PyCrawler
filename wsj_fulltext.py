# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import math
import re

from pycrawler.scraper import encodeurl
from pycrawler.handler import Handler
from pycrawler.utils.toolbox import md5
from pycrawler.spider import Driver
from mongojuice.document import Document


MONTH_NUM = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
             'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
             'January': 1, 'February': 2, 'March': 3, 'April': 4, 'June': 6,
             'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11,
             'December': 12}


class Article(Document):
    structure = {'_id': int,
                 'title': str,
                 'url': str,
                 'content': str,
                 'date': str,
                 'datenum': int,
                 'keyword': str}
    given = ['title', 'url', 'content', 'date', 'keyword']
    database = 'wsj_fulltext'
    collection = 'new_fulltext'

    def __init__(self, title, url, content, date, keyword):
        super(Article, self).__init__()
        self._id = md5(title + date + keyword)
        self.title = title
        self.url = url
        self.content = content
        self.date = date
        self.datenum = self._date2num(date)
        self.keyword = keyword

    def _date2num(self, date):
        parts = date.split(' ')
        try:
            num = (int(parts[2]) * 100 + MONTH_NUM[parts[1]]) * 100 + int(parts[0])
        except IndexError:
            num = 0
        return num


@Handler.register
class Wsj_full_Handler(Handler):
    def __init__(self, spider):
        super(Wsj_full_Handler, self).__init__()
        self._spider = spider
        self.logger = spider.logger
        self.name = spider.name + '-Handler'
        self.args = {'debug': True,
                     'log': True,
                     'logfile': 'Wsj_full_Handler.log',
                     'start': 0}

    def parse(self, html, url):
        url_parts = url.split('/')
        try:
            if url_parts[3] == 'results':
                return self._parse_search(html, url_parts)
            elif url_parts[3] == 'docview':
                return self._parse_article(html, url_parts)
        except IndexError:
            self.logger.error(self.name, 'Unexpected url: ' + url)

    def _parse_search(self, html, url_parts):
        # if url_parts[5] == '1':
        #     self._generate_all_pages(html, url_parts)
        base_url = 'http://search.proquest.com.turing.library.northwestern.edu'
        title_p = re.compile('class="previewTitle Topicsresult".*[0-9]{5}"')
        titles = title_p.findall(html)
        keyword = self._extract_keyword(url_parts)
        urls = []
        if 'start' in self.args and self.args['start'] == 0:
            for title in titles:
                doc_url = title[title.index('href="') + 6: -1]
                doc_url += '&' + keyword
                urls.append(base_url + doc_url)
            if len(urls) == 0:
                self.logger.error(self.name, 'No urls found in: ' + '/'.join(url_parts))
                # self._spider.retire()
            else:
                self.logger.info(self.name, 'Found {0} urls'.format(len(urls)))
        total_p = re.compile('[0-9,]+ Results')
        total = total_p.findall(html)
        if len(total) != 1:
            self.logger.error(self.name, 'Unexpected total string in: ' + '/'.join(url_parts))
        else:
            total = total[0]
            total_str = total.split(' ')[0]
            if ',' in total_str:
                total_str = total_str.replace(',', '')
            total_num = int(total_str)
            page_num = int(url_parts[5])
            if 'start' in self.args and self.args['start'] != 0:
                url_parts[5] = str(self.args['start'])
                urls.append('/'.join(url_parts))
                self.args['start'] = 0
            elif page_num * 20 < total_num:
                url_parts[5] = str(page_num + 1)
                urls.append('/'.join(url_parts))
            else:
                if 'years' in self.args and self.args['years']:
                    year = self.args['years'].pop(0)
                    urls += generate_seeds([keyword], year)
        self._spider.addtask(urls)

    def _generate_all_pages(self, html, url_parts):
        total_p = re.compile('[0-9,]+ Results')
        total = total_p.findall(html)
        if len(total) != 1:
            self.logger.error(self.name, 'Unexpected total string in: ' + '/'.join(url_parts))
        else:
            total = total[0]
            total_str = total.split(' ')[0]
            if ',' in total_str:
                total_str = total_str.replace(',', '')
            total_num = int(total_str)
            pages = int(math.ceil(float(total_num) / 20))
            urls = []
            for i in xrange(2, pages + 1):
                url_parts[5] = str(i)
                urls.append('/'.join(url_parts))
            self._spider.addtask(urls)

    def _parse_article(self, html, url_parts):
        keyword = url_parts[-1].split('&')[-1]
        url_parts[-1] = url_parts[-1].replace('&' + keyword, '')
        url = '/'.join(url_parts)
        title_p = re.compile('<h1 class="ltr">.*</h1>')
        date_p = re.compile('[0-9]{2} [A-Z][a-z]+ [0-9]{4}')
        title = title_p.findall(html)
        if len(title) != 1:
            self.logger.error(self.name, 'Unexpected title in: ' + url)
            # self._spider.retire()
            return None
        title = title[0][16:-5]
        date = date_p.findall(html)
        if len(date) != 1:
            self.logger.error(self.name, 'Unexpected date in:' + url)
            return None
        date = date[0]
        try:
            raw_text = html[html.index('<Text'): html.index('</Text>')]
        except ValueError:
            self.logger.warning(self.name, 'Text not availible in:' + url)
            raw_text = 'Not availible'
            return Article(title, url, raw_text, date, keyword)
        text = re.split('<.+>', raw_text)
        text = [each.strip() for each in text if each.strip() != '']
        content = '\n'.join(text)
        article = Article(title, url, content, date, keyword)
        self.logger.info(self.name, 'Get article with id: ' + str(article._id))
        return article

    def _extract_keyword(self, url_parts):
        args = url_parts[-1].split(',')
        keyword = 'notfound'
        for arg in args:
            if arg.startswith('$22qry$22'):
                keyword_part = arg.split('$22')[3]
                keyword = keyword_part.split('+')[0]
        return keyword


def getCookie():
    data = {'IDToken0': '',
            'IDToken1': 'pmo885',
            'IDToken2': '',
            'IDButton': 'Log In',
            'goto': 'aHR0cHM6Ly9zZXNhbWUubGlicmFyeS5ub3J0aHdlc3Rlcm4uZWR1L2NnaS1iaW4vc3NvRXpwQ2hlY2sucGw'
                    '/dXJsPWV6cC4yYUhSMGNEb3ZMM05sWVhKamFDNXdjbTl4ZFdWemRDNWpiMjB2WVdKcFoyeHZZbUZzTDNCMVl'
                    'teHBZMkYwYVc5dVluSnZkM05sUDJGalkyOTFiblJwWkQweE1qZzJNUS0t',
            'SunQueryParamsString': '',
            'encoded': 'true',
            'gx_charset': 'UTF-8'}
    url = 'https://websso.it.northwestern.edu/amserver/UI/Login'

    cookie = cookielib.MozillaCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    res = opener.open(url, urllib.urlencode(data))
    res.close()
    return cookie


def generate_seeds(keywords, year):
    baseurl = 'http://search.proquest.com.turing.library.northwestern.edu/index.expandedbasicsearchbox_0.searchform'
    formdata = {'t:ac': '5D5F265CA8DC461DPQ',
                't:submit': '["expandedSearch",""]',
                't:formdata': 'asKmtyg4x6Ls+6cDSptwNqyredw=:H4sIAAAAAAAAAKWTvUoEMRSFr4uCKCoINtZaiJi10EZZRBBBGFTctZZM5rpGM0l'
                              'MsjtjY6uFlQ/gE4gvsYWdlS/gAwhWViJmMviH+LPYhS/JOYd7kst76MumYWpNJpgvYK6pXyQxtZxZpIbtxSrfmSXl2qF'
                              'JrYF5ZZqEasr2kDiq0TpzNE+YMih4TPxdJMuxh5S5VY4imaija+nJ7c7g3dj1UwV6IhhkSjqjxDpN0cFotE/btCqobFb'
                              'rznDZXMy1g4HSteFdu4243G3ETaMYWltvxSm3livZuUrmdh8vbioAuc6qMPOL/etGyXyEGlMp0UYdtry7z6Ltm7/f0Uq'
                              'idJYEQ/fV/uJ2uvdsuP1QgUoE/Uxwf3otOYTjMD0UmHpQTC+gYlrDrwnqIUHB+7MaLP5pbIL7FGgs2W0J4TB3AdhCBBw'
                              'MFbThaVTQf4oWmn3ZEtS609CIxmCbY/Yp2kjBtwIvw/1XuIz3+3MTXB7YUJ7veuXH5/ah7sjf+q7yDX56/jx+IsMH+Vx'
                              '5+A3vji8/owjltQMAAA==',
                'searchTerm': ''}
    search = '{0} AND PUBID(105983) AND YR(<={1}) AND YR(>={1})'
    urls = []
    for keyword in keywords:
        formdata['searchTerm'] = search.format(keyword, year)
        urls.append(encodeurl('POST', baseurl, formdata))
    return urls


DriverSettings = {'name': 'Wsj_Fulltext_Crawler',
                  'spiders': [
                      {'name': 'NewFulltextSpider',
                       'speed': 1,
                       'delay': 30,
                       'scraper': {'name': 'DefaultCookieScraper',
                                   'args': {'getCookie': getCookie}},
                       'frontier': {'name': 'BFSFrontier'},
                       'handlers': [{'name': 'Wsj_full_Handler',
                                     'args': {'start': 0,
                                              'years': [2011, 2012, 2013, 2014, 2015]}}]}]}


def main():
    driver = Driver(DriverSettings)
    seeds = generate_seeds(['apple'], 2010)
    driver.addtask('NewFulltextSpider', seeds, force=True)
    driver.start()


if __name__ == '__main__':
    main()

__author__ = 'mengpeng'
import urllib


class Task(object):

    def __init__(self, url, params=None, timeout=5):
        self._url = url
        self._params = params
        self._timeout = timeout
        self.timeout = timeout

    @property
    def url(self):
        pass

    @url.getter
    def url(self):
        fullurl = self._url
        try:
            fullurl += '?' + urllib.urlencode(self._params)
        except TypeError as error:
            print(error)
        return fullurl

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if value < 0:
            self._timeout = 5
        elif value > 10:
            self._timeout = 10
        else:
            self._timeout = value
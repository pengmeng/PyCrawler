__author__ = 'mengpeng'
import urllib.parse
from enum import Enum, unique


@unique
class Priority(Enum):
    Low = 0
    Normal = 1
    High = 2


class Task(object):

    def __init__(self, url, params=None, timeout=5, priority=Priority.Normal):
        self._url = url
        self._params = params
        self._timeout = timeout
        self.timeout = timeout
        self._priority = priority
        self.priority = priority

    @property
    def url(self):
        pass

    @url.getter
    def url(self):
        fullurl = self._url
        try:
            fullurl = self._url + '?' + urllib.parse.urlencode(self._params)
        except TypeError as error:
            pass
        finally:
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

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = value if isinstance(value, Priority) else Priority.Normal
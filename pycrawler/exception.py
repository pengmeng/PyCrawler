__author__ = 'mengpeng'


class PyCrawlerException(Exception):
    pass


class ScraperException(PyCrawlerException):
    pass


class HandlerException(PyCrawlerException):
    pass


class FrontierException(PyCrawlerException):
    pass


class PersistException(PyCrawlerException):
    pass
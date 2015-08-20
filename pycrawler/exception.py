# -*- coding: utf-8 -*-
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


class NotifierException(PyCrawlerException):
    pass

# -*- coding: utf-8 -*-
__author__ = 'mengpeng'
import time


def gethash(string, cap=0xffffffff):
    return hash(string) & cap


def timestamp():
    return time.strftime("%H:%M:%S", time.localtime(time.time()))


def datestamp():
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


def fullstamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

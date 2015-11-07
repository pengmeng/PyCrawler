# -*- coding: utf-8 -*-
__author__ = 'mengpeng'
import time
import hashlib


def gethash(string, cap=0xffffffff):
    return hash(string) & cap


def timestamp():
    return time.strftime("%H:%M:%S", time.localtime(time.time()))


def datestamp():
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


def fullstamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def md5(string, hex_digest=True):
    """Return md5 of the string

    Keyword arguments:
    hex_digest -- return md5 in hex or not (default True)
    """
    return _crypt('md5', string, hex_digest)


def _crypt(algorithm, string, hex_digest=True):
    """Cryption helper funciton"""
    cryptor = hashlib.new(algorithm, string)
    return cryptor.hexdigest() if hex_digest else cryptor.digest()


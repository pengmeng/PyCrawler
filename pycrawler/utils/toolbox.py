# -*- coding: utf-8 -*-
"""
Small useful tools for general purpose

requirement:
    Python 2.7
"""

import csv
import time
import json
import hashlib

import os


# File system tools

def mkdir(original_dir):
    """Return original dir with os.sep if not ends with it and make this dir if not exists."""
    if '~' in original_dir:
        original_dir = os.path.expanduser(original_dir)
    if not os.path.isdir(original_dir):
        os.makedirs(original_dir)
    if not original_dir.endswith(os.sep):
        original_dir += os.sep
    return original_dir


def split_path_name_ext(full_path):
    """Return path name extension of the file from its full path."""
    path_name, ext = os.path.splitext(full_path)
    path, name = os.path.split(path_name)
    return path, name, ext


def mapfile(func, top_dir, recursive=True):
    """Call func(file) for each file in top directory and return the list of results.

    Keyword arguments:
    recursive -- traverse files in the subdir (default True)
    """
    if '~' in top_dir:
        top_dir = os.path.expanduser(top_dir)
    if not os.path.isdir(top_dir):
        return None
    children = os.walk(top_dir)
    result = []
    if not recursive:
        children = [next(children)]
    for dir_path, _, files in children:
        for each in files:
            file_path = os.path.join(dir_path, each)
            result.append(func(file_path))
    return result


def loadtxt(file_path, trim=None, header=False, ignore_empty_line=False):
    """Return firstline, lines if header is True and lines if header is False
    Keyword arguments:
    trim -- chars that will be used by str.strip() (default None)
    header -- return first line seperately (default False)
    ignore_empty_line -- exclude lines that is equal '' after strip() (default False)
    """
    lines = []
    with open(file_path, 'r') as infile:
        first = infile.readline().strip(trim) if header else None
        for line in infile.readlines():
            line = line.strip(trim)
            if ignore_empty_line and line == '':
                continue
            lines.append(line)
    if header:
        return first, lines
    else:
        return lines


def dumptxt(file_path, lines, mode='w', header=None):
    """Write lines into file line by line (auto append '\\n' for each line)
    Keyword arguments:
    mode -- write mode (default 'w')
    header -- first line to write, usually useless in this funciton (default None)
    """
    with open(file_path, mode) as outfile:
        if header:
            outfile.writeline(header + '\n')
        for line in iter(lines):
            outfile.write(line + '\n')


def loadcsv(file_path, header=False, ignore_empty_line=False, **kwargs):
    """CSV version of loadtxt"""
    lines = []
    with open(file_path, 'r') as infile:
        for each in csv.reader(infile, **kwargs):
            if ignore_empty_line and not each:
                continue
            lines.append(each)
    if header:
        return lines[0], lines[1:]
    else:
        return lines


def dumpcsv(file_path, lines, mode='w', header=None, **kwargs):
    """CSV version of dumptxt"""
    with open(file_path, mode) as outfile:
        writer = csv.writer(outfile, **kwargs)
        if header:
            writer.writerow(header)
        writer.writerows(lines)


def loadjson(file_path, encoding='utf8', **kwargs):
    """JSON version of loadtxt
    Return:
    json data as Python object

    Keyword arguments:
    encoding: file encoding
    """
    with open(file_path, 'r') as infile:
        obj = json.load(infile, encoding=encoding, **kwargs)
    return obj


def dumpjson(file_path, obj, encoding='utf8', ensure_ascii=False, pretty=False, **kwargs):
    """JSON version of dumptxt"""
    with open(file_path, 'w') as outfile:
        if pretty:
            json.dump(obj, outfile, encoding=encoding, ensure_ascii=ensure_ascii,
                      indent=4, separators=(',', ': '), **kwargs)
        else:
            json.dump(obj, outfile, encoding=encoding, ensure_ascii=ensure_ascii, **kwargs)


# Hashlib wrappers to encrypt easily

def gethash(string, cap=0xffffffff):
    """Return the buildin hash of the string & cap

    Keyword arguments:
    cap -- value that will & with hash code (default 0xffffffff)
    """
    return hash(string) & cap


def md5(string, hex_digest=True):
    """Return md5 of the string

    Keyword arguments:
    hex_digest -- return md5 in hex or not (default True)
    """
    return _crypt('md5', string, hex_digest)


def sha1(string, hex_digest=True):
    """Return sha1 of the string

    Keyword arguments:
    hex_digest -- return sha1 in hex or not (default True)
    """
    return _crypt('sha1', string, hex_digest)


def sha256(string, hex_digest=True):
    """Return sha256 of the string

    Keyword arguments:
    hex_digest -- return sha256 in hex or not (default True)
    """
    return _crypt('sha256', string, hex_digest)


def sha512(string, hex_digest=True):
    """Return sha512 of the string

    Keyword arguments:
    hex_digest -- return sha512 in hex or not (default True)
    """
    return _crypt('sha512', string, hex_digest)


def _crypt(algorithm, string, hex_digest=True):
    """Cryption helper funciton"""
    cryptor = hashlib.new(algorithm, string)
    return cryptor.hexdigest() if hex_digest else cryptor.digest()


# Date and time tools

def timestamp(fmt='%H:%M:%S'):
    """Return current time stamp with specific format"""
    return _stamp(fmt)


def datestamp(fmt='%Y-%m-%d'):
    """Return current date stamp with specific format"""
    return _stamp(fmt)


def fullstamp(fmt='%Y-%m-%d %H:%M:%S'):
    """Return full stamp including date and time with specific format"""
    return _stamp(fmt)


def _stamp(fmt):
    """Time stamp helper funtion"""
    return time.strftime(fmt, time.localtime())


# Data processing

def join(fulllist, filterlist, complementary=False):
    """Using second list filter first list, return the intersection of two lists
    or complementary set of intersection with first list as universe.

    Keyword arguments:
    complementary -- return complementary set of intersection
    """
    if not isinstance(fulllist, list) or not isinstance(filterlist, list):
        raise TypeError('Onlt support list at present.')
    fullset, filterset = set(fulllist), set(filterlist)
    intersection = fullset & filterset
    result = fullset - intersection if complementary else intersection
    return result


def join_remain(fulllist, filterlist, complementary=False):
    """Using second list filter first list, return the intersection of two lists
    or complementary set of intersection with first list as universe
    and remain lists of the two in sequence.

    Return:
    intersection, first_remaining, second_remaining

    Keyword arguments:
    complementary -- return complementary set of intersection
    """
    if not isinstance(fulllist, list) or not isinstance(filterlist, list):
        raise TypeError('Only support list at present.')
    fullset, filterset = set(fulllist), set(filterlist)
    intersection = fullset & filterset
    remain = fullset - intersection
    full_intersection = remain if complementary else intersection
    full_remain = intersection if complementary else remain
    filter_remain = filterset - intersection
    return list(full_intersection), list(full_remain), list(filter_remain)

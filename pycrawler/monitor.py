# -*- coding: utf-8 -*-
import json
import copy
from threading import Thread

from utils.tcpecho import Server


class Monitor(object):
    def __init__(self, driver, host, port, newthread=False):
        self.driver = driver
        self.server = Server(host, port, newthread)

    def start(self):
        self.server.callback = lambda client, addr, data: _Handler(self.driver, client, addr, data).start()
        self.server.start()


class _Handler(Thread):
    def __init__(self, driver, client, addr, data):
        super(_Handler, self).__init__()
        self.driver = driver
        self.client = client
        self.addr = addr
        self.data = data

    def run(self):
        try:
            cmd = self._data2json()
            parts = self._parsecommand(cmd)
            self._executecmd(*parts)
        finally:
            self._exit()

    def _exit(self):
        self.client.close()
        exit(0)

    def _response(self, result):
        self.client.send(result)

    def _data2json(self):
        try:
            cmd = json.loads(self.data)
            return cmd
        except ValueError:
            print('Parse json string failed, discard: ' + self.data)
            self._response('{"error": "Bad Request", "reason": "broken json string"}')
            self._exit()

    def _parsecommand(self, cmd):
        if 'type' in cmd and 'action' in cmd:
            _type, _action, _args = cmd['type'], cmd['action'], cmd.get('args')
            return _type, _action, _args
        else:
            self._response('{"error": "Bad Request", "reason": "missing type or action"}')
            self._exit()

    def _executecmd(self, _type, _action, _args):
        if _type == 'ask':
            result = self._execask(_action, _args)
        elif _type == 'do':
            result = self._execdo(_action, _args)
        else:
            result = '{"error": "Argument Error", "reason": "unknown request type:' + _type + '"}'
        self._response(result)

    def _execask(self, _action, _args):
        if _action == 'init':
            result = copy.deepcopy(self.driver.config)
        elif _action == 'summary':
            result = {'status': 'ok',
                      'driver': self.driver.name,
                      'spiders': []}
            if not _args:
                for each in self.driver.getspiders():
                    temp = each.summary()
                    temp['name'] = each.name
                    result['spiders'].append(temp)
            elif isinstance(_args, list):
                for each in _args:
                    spider = self.driver.getspider(each)
                    if spider:
                        temp = spider.summary()
                        temp['name'] = each
                        result['spiders'].append(temp)
            else:
                result = {'error': 'Argument Error',
                          'reason': 'args must be None or list'}
        else:
            result = {'error': 'Argument Error', 'reason': 'unknown request action:{0}'.format(_action)}
        return json.dumps(result)

    def _execdo(self, _action, _args):
        func = self._getfunc(_action)
        result = {'status': 'ok'}
        if func:
            if not _args:
                map(func, self.driver.getspiders())
            elif isinstance(_args, list):
                map(lambda x: func(self.driver.getspider(x)), _args)
            else:
                result = {'error': 'Argument Error',
                          'reason': 'args must be None or list'}
        else:
            result = {'error': 'Argument Error', 'reason': 'unknown request action:{0}'.format(_action)}
        return json.dumps(result)

    def _getfunc(self, _action):
        func = None
        if _action == 'start':
            func = lambda spider: spider.start()
        elif _action == 'pause':
            func = lambda spider: spider.pause()
        elif _action == 'resume':
            func = lambda spider: spider.resume()
        elif _action == 'stop':
            func = lambda spider: spider.retire()
        return func and (lambda spider: spider and func(spider))

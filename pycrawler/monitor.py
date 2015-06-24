__author__ = 'mengpeng'
from threading import Thread
from utils.tcpecho import Server


class Monitor(object):
    def __init__(self, driver, host, port, newthread=False):
        self.driver = driver
        self.server = Server(host, port, newthread)

    def start(self):
        self.server.callback = lambda client, addr, data: Monitor.Handler(client, addr, data).start()
        self.server.start()

    class Handler(Thread):
        def __init__(self, client, addr, data):
            super(Monitor.Handler, self).__init__()
            self.client = client
            self.addr = addr
            self.data = data

        def run(self):
            pass
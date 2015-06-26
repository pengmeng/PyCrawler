__author__ = 'mengpeng'
import socket
from threading import Thread


class Server(Thread):
    def __init__(self, host, port, newthread=False, callback=None):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.newthread = newthread
        self.callback = callback
        self.keep = True

    def start(self):
        if self.newthread:
            super(Server, self).start()
        else:
            self.run()

    def run(self):
        s = socket.socket()
        try:
            s.bind((self.host, self.port))
            s.listen(5)
            while self.keep:
                client, addr = s.accept()
                self.serve(client, addr)
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
        except socket.error as e:
            print(e)
        finally:
            print('shut down')
            s.close()

    def serve(self, client, addr):
        data = client.recv(1024)
        if data:
            if self.callback:
                self.callback(client, addr, data)
            else:
                print(data)
        else:
            client.close()

    def stop(self):
        if self.keep:
            self.keep = False
            s = socket.socket()
            try:
                s.connect((self.host, self.port))
                s.send('')
            except socket.error as e:
                print(e)
            finally:
                s.close()


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def tell(self, message, wait=True):
        s = socket.socket()
        response = None
        try:
            s.connect((self.host, self.port))
            s.sendall(message)
            response = self._receive(s) if wait else None
        except socket.error as e:
            print(e)
        finally:
            s.close()
        return response

    def _receive(self, s):
        data = s.recv(1024)
        return data
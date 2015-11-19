# -*- coding: utf-8 -*-
import smtplib

from pycrawler.exception import NotifierException


class Notifier(object):
    Dict = {}

    def __init__(self):
        self.args = None

    @staticmethod
    def register(cls):
        if isinstance(cls, type):
            Notifier.Dict[cls.__name__] = cls
            return cls
        else:
            raise NotifierException('Must register notifier with class name')

    @staticmethod
    def get(name):
        if name in Notifier.Dict:
            return Notifier.Dict[name]
        else:
            raise NotifierException('No notifier class named ' + name)

    def setargs(self, args):
        if not isinstance(args, dict):
            raise NotifierException('Args must be a dict')
        for key, value in args.iteritems():
            self.args[key] = value

    def notify(self, *args):
        raise NotImplementedError


@Notifier.register
class EmailNotifier(Notifier):
    def __init__(self, spider):
        super(EmailNotifier, self).__init__()
        self._spider = spider
        self.logger = spider.logger
        self.name = spider.name + '-Notifier'
        self.args = {'server': 'smtp.gmail.com',
                     'port': 587,
                     'protocol': 'smtp',
                     'username': 'pycrawler.notification@gmail.com',
                     'password': ''}

    def notify(self, receiver, subject, content):
        user = self.args['username']
        pwd = self.args['password']
        server = self.args['server']
        port = self.args['port']
        FROM = user
        TO = receiver if isinstance(receiver, list) else [receiver]
        message = 'From: {0}\r\nTo: {1}\r\nSubject: {2}\r\n\r\n{3}'.format(FROM, ', '.join(TO), subject, content)
        try:
            server = smtplib.SMTP(server, port)
            server.ehlo()
            server.starttls()
            server.login(user, pwd)
            server.sendmail(FROM, TO, message)
            server.close()
            self.logger.info(self.name, 'Notify {0} via email'.format(', '.join(TO)))
        except Exception as e:
            self.logger.error(self.name, e.message)

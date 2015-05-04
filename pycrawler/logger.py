__author__ = 'mengpeng'
import os
import logging
import logging.config
from pycrawler.utils.tools import datestamp

LoggingConfig = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'Default-file': {
            'filename': './log/Default-'+datestamp()+'.log',
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'formatter': 'default'
        },
        'Default-console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'loggers': {
        'Default-logger': {
            'handlers': ['Default-file', 'Default-console'],
            'level': 'DEBUG'
        }
    }
}


class Logger(object):
    def __init__(self, name):
        self.name = name
        self._logger = logging.getLogger(name+'-logger')

    @staticmethod
    def register(modulename, consolelog=True, consolelevel='DEBUG', filelog=True, filelevel='WARNING'):
        name = modulename+'-logger'
        LoggingConfig['loggers'][name] = {'handlers': [], 'level': 'DEBUG'}
        if filelog:
            LoggingConfig['handlers'][modulename+'-file'] = {'filename': './log/'+modulename+'-'+datestamp()+'.log',
                                                             'level': filelevel,
                                                             'class': 'logging.FileHandler',
                                                             'formatter': 'default'}
            LoggingConfig['loggers'][name]['handlers'].append(modulename+'-file')
        if consolelog:
            LoggingConfig['handlers'][modulename+'-console'] = {'level': consolelevel,
                                                                'class': 'logging.StreamHandler',
                                                                'formatter': 'default'}
            LoggingConfig['loggers'][name]['handlers'].append(modulename+'-console')

    @staticmethod
    def load():
        if not os.path.exists('./log/'):
            os.mkdir('./log/')
        logging.config.dictConfig(LoggingConfig)

    def debug(self, location, message):
        self._logger.debug(self._fmt(location, message))

    def info(self, location, message):
        self._logger.info(self._fmt(location, message))

    def warning(self, location, message):
        self._logger.warning(self._fmt(location, message))

    def error(self, location, message):
        self._logger.error(self._fmt(location, message))

    def _fmt(self, location, message):
        return '['+location+'] '+message
# -*- coding: utf-8 -*-
import logging
from unittest import TestCase
from pycrawler.logger import Logger
from pycrawler.logger import LoggingConfig


class TestLogger(TestCase):
    def test_register(self):
        Logger.register('Test')
        self.assertIn('Test-logger', LoggingConfig['loggers'])
        self.assertIn('Test-file', LoggingConfig['handlers'])
        self.assertIn('Test-console', LoggingConfig['handlers'])

    def test_load(self):
        Logger.load()
        logger = Logger('Default')
        self.assertIsInstance(logger._logger, logging.Logger)

    def test_debug(self):
        Logger.load()
        logger = Logger('Default')
        logger.debug('unittest', 'testdebug')

    def test_info(self):
        Logger.load()
        logger = Logger('Default')
        logger.info('unittest', 'testinfo')

    def test_warning(self):
        Logger.load()
        logger = Logger('Default')
        logger.warning('unittest', 'testwarning')

    def test_error(self):
        Logger.load()
        logger = Logger('Default')
        logger.error('unittest', 'testerror')

    def test__fmt(self):
        Logger.load()
        logger = Logger('Default')
        self.assertEqual('[test] test', logger._fmt('test', 'test'))

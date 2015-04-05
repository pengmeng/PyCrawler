__author__ = 'mengpeng'
from unittest import TestCase
from pycrawler.scraper import Scraper
from pycrawler.scraper import DefaultScraper
from pycrawler.exception import ScraperException


class TestScraper(TestCase):
    def test_register(self):
        self.assertRaises(ScraperException, Scraper.register, 0)
        self.assertEqual(DefaultScraper, Scraper.Dict['DefaultScraper'])

    def test_getScraper(self):
        self.assertRaises(ScraperException, Scraper.getScraper, 'None')
        self.assertEqual(DefaultScraper, Scraper.getScraper('DefaultScraper'))
        self.assertIsInstance(Scraper.getScraper('DefaultScraper')(), DefaultScraper)
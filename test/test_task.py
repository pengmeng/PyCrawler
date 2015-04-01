__author__ = 'mengpeng'
from unittest import TestCase
from pycrawler.task import Task
from pycrawler.task import Priority


class TestTask(TestCase):
    def test_url(self):
        task = Task('sample-url', {'a': '1'})
        self.assertEqual('sample-url?a=1', task.url)
        task = Task('sample-url', 1)
        self.assertEqual('sample-url', task.url)

    def test_priority(self):
        self.assertNotEqual(0, Priority.Low)
        self.assertEqual(1, Priority.Normal.value)
        self.assertTrue(isinstance(Priority.High, Priority))
        task = Task('sample', priority=6)
        self.assertEqual(Priority.Normal, task.priority)
        task.priority = 5
        self.assertEqual(Priority.Normal, task.priority)

    def test_timeout(self):
        task = Task('sample', timeout=100)
        self.assertEqual(10, task.timeout)
        task.timeout = 3
        self.assertEqual(3, task.timeout)
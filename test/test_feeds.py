"""Tests for the Feeds module"""

import unittest
import sys
from feeds.feed_server import feeds_list
sys.path.append("/opt/pkppln/feeds")


class TestFeeds(unittest.TestCase):

    def test_foo(self):
        self.assertTrue(True, 'yes')

    def test_list(self):
        self.assertEqual('hello world.', feeds_list(),  'feeds list returns')

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

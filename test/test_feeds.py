"""Tests for the Feeds module"""

import unittest
import sys
import xml.etree.ElementTree as ET
import json
from os.path import abspath, dirname
sys.path.append(dirname(dirname(abspath(__file__))))
from feeds.feed_server import terms_feed, get_config, get_connection
import MySQLdb.cursors


class TestFeeds(unittest.TestCase):

    """
    Class to test the feeds generator. Doesn't attempt to test the WSGI
    stuff at all, as that's just a thin wrapper around feeds_server.py
    """

    def test_get_config(self):
        """
        Get a config object, and check that a required
        field is present.
        """
        config = get_config()
        try:
            config.get('Database', 'db_host')
        except Exception:
            self.fail('Cannot find Database.db_host config.')

    def test_get_connection(self):
        """
        Get a database cursor.
        """
        connection = get_connection()
        self.assertIsInstance(connection, MySQLdb.cursors.DictCursor)

    def test_terms_rss(self):
        """
        Generate an RSS feed. Verifies that the feed contains a known
        string, and that it has more than zero item elements.
        """
        content = str(terms_feed('rss'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content)
        self.assertEquals('rss', root.tag)
        self.assertGreater(len(root.findall('.//item')), 0)

    def test_terms_atom(self):
        """
        Generate an Atom Feed. Verifies that the feed contains a
        known string, and that it has more than zero entry elements.
        """
        content = str(terms_feed('atom'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content)
        # must use full namespace here.
        self.assertEquals('{http://www.w3.org/2005/Atom}feed', root.tag)
        self.assertGreater(
            len(root.findall('.//{http://www.w3.org/2005/Atom}entry')),
            0
        )

    def test_terms_json(self):
        """
        Generate a JSON feed.
        """
        content = str(terms_feed('json'))
        self.assertGreater(len(content), 0)
        root = json.loads(content)
        self.assertGreater(len(root), 0)

    def test_terms_error(self):
        """
        Attempt to generate an invalid feed.
        """
        response = terms_feed('fooooooo')
        self.assertEquals('404 Not Found', response.status)
        self.assertEquals('', str(response))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

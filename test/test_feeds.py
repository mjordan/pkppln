#!/usr/bin/env python
# -*- coding: <encoding name> -*-

"""Tests for the Feeds module"""

import unittest
import sys
import xml.etree.ElementTree as ET
import json
from os.path import abspath, dirname
from _elementtree import XMLParser
sys.path.append(dirname(dirname(abspath(__file__))))
from feeds.feed_server import terms_feed, get_config, get_connection
import MySQLdb.cursors
import requests

with_server = False


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
        content = unicode(terms_feed('rss'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content.encode('UTF-8'), parser=XMLParser(encoding='UTF-8'))
        self.assertEquals('rss', root.tag)
        self.assertGreater(len(root.findall('.//item')), 0)

    def test_terms_atom(self):
        """
        Generate an Atom Feed. Verifies that the feed contains a
        known string, and that it has more than zero entry elements.
        """
        content = unicode(terms_feed('atom'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content.encode('UTF-8'), parser=XMLParser(encoding='UTF-8'))
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
        content = unicode(terms_feed('json'))
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

    def test_server_json(self):
        """
        Get a JSON feed from the server (which should have been loaded from
        pkpplntest.sql) and parse it as JSON. It contains a bunch of
        unicode characters (incl. some problematic ones in the past) and check
        the content.
        """
        if not with_server:
            return
        r = requests.get('http://localhost:8080/terms/json')
        self.assertEquals('application/json; charset=utf-8', r.headers['content-type'])
        js = json.loads(r.content)
        self.assertEquals(len(js), 5)
        self.assertEquals(js[0]['description'], 'I am good to go.')
        self.assertEquals(js[1]['description'], u'U+00E9: \xe9')
        self.assertEquals(js[2]['description'], u'U+20AC: \u20AC')
        self.assertEquals(js[3]['description'], u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(js[4]['description'], u'U+2039 U+203A: \u2039\u203a')

    def test_server_atom(self):
        if not with_server:
            return
        r = requests.get('http://localhost:8080/terms/atom')
        self.assertEquals('text/xml; charset=utf-8', r.headers['content-type'])
        root = ET.fromstring(r.content, parser=XMLParser(encoding='UTF-8'))
        entries = root.findall('.//{http://www.w3.org/2005/Atom}content')
        self.assertEquals(entries[0].text.strip(), u'I am good to go.')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(entries[3].text.strip(), u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(entries[4].text.strip(), u'U+2039 U+203A: \u2039\u203a')

    def test_server_rss(self):
        if not with_server:
            return
        r = requests.get('http://localhost:8080/terms/rss')
        self.assertEquals('text/xml; charset=utf-8', r.headers['content-type'])
        root = ET.fromstring(r.content, parser=XMLParser(encoding='UTF-8'))
        entries = root.findall('.//item/description')
        self.assertEquals(entries[0].text.strip(), u'I am good to go.')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(entries[3].text.strip(), u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(entries[4].text.strip(), u'U+2039 U+203A: \u2039\u203a')

if __name__ == '__main__':  # pragma: no cover
    if '--server' in sys.argv:
        with_server = True
        sys.argv.remove('--server')
    unittest.main()

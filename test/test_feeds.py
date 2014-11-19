"""Tests for the Feeds module"""

import unittest
import sys
import xml.etree.ElementTree as ET
import json
import urllib2
from urllib2 import URLError, HTTPError
sys.path.append("/opt/pkppln")
from feeds.feed_server import terms_feed


class TestFeeds(unittest.TestCase):

    def test_terms_rss(self):
        content = str(terms_feed('rss'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content)
        self.assertEquals('rss', root.tag)
        self.assertGreater(len(root.findall('.//item')), 0)

    def test_terms_atom(self):
        content = str(terms_feed('atom'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content)
        # must use full namespace here.
        self.assertEquals('{http://www.w3.org/2005/Atom}feed', root.tag)
        self.assertGreater(len(root.findall('.//{http://www.w3.org/2005/Atom}entry')), 0)        

    def test_terms_json(self):
        content = str(terms_feed('json'))
        self.assertGreater(len(content), 0)
        root = json.loads(content)
        self.assertGreater(len(root), 0)

    def test_bottle_terms_rss(self):
        url = 'http://localhost:8080/terms/rss'
        try:
            response = urllib2.urlopen(url)
        except HTTPError as e:
            self.fail('HTTP ' + str(e.code) + ' for ' + url)
        except URLError as e:
            self.fail('Cannot connect ' + url + ' ' + str(e.reason))
        content = response.read()
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content)
        self.assertEquals('rss', root.tag)
        self.assertGreater(len(root.findall('.//item')), 0)

    def test_bottle_terms_atom(self):
        url = 'http://localhost:8080/terms/atom'
        try:
            response = urllib2.urlopen(url)
        except HTTPError as e:
            self.fail('HTTP ' + str(e.code) + ' for ' + url)
        except URLError as e:
            self.fail('Cannot connect ' + url + ' ' + str(e.reason))
        content = response.read()
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(content)
        # must use full namespace here.
        self.assertEquals('{http://www.w3.org/2005/Atom}feed', root.tag)
        self.assertGreater(len(root.findall('.//{http://www.w3.org/2005/Atom}entry')), 0)        

    def test_bottle_terms_json(self):
        url = 'http://localhost:8080/terms/json'
        try:
            response = urllib2.urlopen(url)
        except HTTPError as e:
            self.fail('HTTP ' + str(e.code) + ' for ' + url)
        except URLError as e:
            self.fail('Cannot connect ' + url + ' ' + str(e.reason))
        content = response.read()
        self.assertGreater(len(content), 0)
        root = json.loads(content)
        self.assertGreater(len(root), 0)

    def test_bottle_format_not_found(self):
        url = 'http://localhost:8080/terms/fooooooooooooooo'
        try:
            urllib2.urlopen(url)
        except HTTPError as e:
            self.assertEqual(404, e.code)
            return
        except e:
            self.fail('Expected HTTP error. Received ' + str(e))
            return
        self.fail('No error received.')

    def test_bottle_error(self):
        url = 'http://localhost:8080/notapufferfish'
        try:
            urllib2.urlopen(url)
        except HTTPError as e:
            self.assertEqual(404, e.code)
            return
        except e:
            self.fail('Expected HTTP error. Received ' + str(e))
            return
        self.fail('No error received.')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

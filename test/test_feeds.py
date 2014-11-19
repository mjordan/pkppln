"""Tests for the Feeds module"""

import unittest
import sys
import xml.etree.ElementTree as ET
import json
sys.path.append("/opt/pkppln")
from feeds.feed_server import terms_feed


class TestFeeds(unittest.TestCase):

    def test_terms_rss(self):
        rss = str(terms_feed('rss'))
        self.assertTrue('PKP PLN Terms' in rss)
        root = ET.fromstring(rss)
        self.assertEquals('rss', root.tag)
        self.assertGreater(len(root.findall('.//item')), 0)

    def test_terms_atom(self):
        atom = str(terms_feed('atom'))
        self.assertTrue('PKP PLN Terms' in atom)
        root = ET.fromstring(atom)
        # must use full namespace here.
        self.assertEquals('{http://www.w3.org/2005/Atom}feed', root.tag)
        self.assertGreater(len(root.findall('.//{http://www.w3.org/2005/Atom}entry')), 0)        

    def test_terms_json(self):
        jsonStr = str(terms_feed('json'))
        self.assertGreater(len(jsonStr), 0)
        root = json.loads(jsonStr)
        self.assertGreater(len(root), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

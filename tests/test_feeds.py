"""Tests for the Feeds module"""

import unittest
import sys
import json
from os.path import abspath, dirname
from lxml import etree as ET

sys.path.append(dirname(dirname(abspath(__file__))))
from webapp.feeds.feed_server import FeedsApp
import pkppln

parser = ET.XMLParser()

class TestFeeds(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        super(TestFeeds, self).setUpClass()
        self.app = FeedsApp("Feeds")

    @classmethod
    def tearDownClass(self):
        super(TestFeeds, self).tearDownClass()
        self.app = None

    def test_setup(self):
        self.assertIsInstance(self.app, FeedsApp, "Saved a feeds app for use.")

    def test_mimetype(self):
        self.assertEquals(self.app.mimetype('atom'), 'text/xml; charset=utf-8')
        self.assertEquals(self.app.mimetype('rss'), 'text/xml; charset=utf-8')
        self.assertEquals(self.app.mimetype('json'), 'application/json; charset=utf-8')
        self.assertEquals(self.app.mimetype('foo'), 'text/plain')

    def test_feeds_index(self):
        index = self.app.feeds_index()
        self.assertGreater(len(index), 0)

    def test_terms_rss(self):
        """
        Generate an RSS feed. Verifies that the feed contains a known
        string, and that it has more than zero item elements.
        """
        content = unicode(self.app.terms_feed('rss'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(
            content.encode('UTF-8'), parser=parser)
        self.assertEquals('rss', root.tag)
        self.assertGreater(len(root.findall('.//item')), 0)

    def test_terms_atom(self):
        """
        Generate an Atom Feed. Verifies that the feed contains a
        known string, and that it has more than zero entry elements.
        """
        content = unicode(self.app.terms_feed('atom'))
        self.assertTrue('PKP PLN Terms' in content)
        root = ET.fromstring(
            content.encode('UTF-8'), parser=parser)
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
        content = unicode(self.app.terms_feed('json'))
        self.assertGreater(len(content), 0)
        root = json.loads(content)
        self.assertGreater(len(root), 0)

    def test_terms_error(self):
        """
        Attempt to generate an invalid feed.
        """
        response = self.app.terms_feed('foofoo')
        self.assertEquals('404 Not Found', response.status)
        self.assertEquals('', str(response))

    def test_server_json(self):
        r = self.app.terms_feed('json')
        js = json.loads(r)
        self.assertEquals(len(js), 5)
        self.assertEquals(js[0]['description'], 'I am good to go.')
        self.assertEquals(js[1]['description'], u'U+00E9: \xe9')
        self.assertEquals(js[2]['description'], u'U+20AC: \u20AC')
        self.assertEquals(js[3]['description'], u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(js[4]['description'], u'U+2039 U+203A: \u2039\u203a')

    def test_server_atom(self):
        r = self.app.terms_feed('atom')
        root = ET.fromstring(r.encode('utf-8'))
        entries = root.findall('.//{http://www.w3.org/2005/Atom}content')
        self.assertEquals(entries[0].text.strip(), u'I am good to go.')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(
            entries[3].text.strip(), u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(
            entries[4].text.strip(), u'U+2039 U+203A: \u2039\u203a')

    def test_server_rss(self):
        r = self.app.terms_feed('rss')
        root = ET.fromstring(r.encode('utf-8'))
        entries = root.findall('.//item/description')
        self.assertEquals(entries[0].text.strip(), u'I am good to go.')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(
            entries[3].text.strip(), u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(
            entries[4].text.strip(), u'U+2039 U+203A: \u2039\u203a')

    def test_server_rss_lang(self):
        r = self.app.terms_feed('rss', 'en-CA')
        root = ET.fromstring(r.encode('utf-8'))
        lang = root.findall('.//language')
        self.assertEquals(1, len(lang))
        self.assertEquals('en-CA', lang[0].text)
        entries = root.findall('.//item/description')
        self.assertEquals(entries[0].text.strip(), u'I am good to go Canada')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9 Canada')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(
            entries[3].text.strip(), u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(
            entries[4].text.strip(), u'U+2039 U+203A: \u2039\u203a')

    def test_server_atom_lang(self):
        r = self.app.terms_feed('atom', 'en-CA')
        root = ET.fromstring(r.encode('utf-8'))
        self.assertEquals('en-CA', root.xpath('//@xml:lang')[0])
        entries = root.findall('.//{http://www.w3.org/2005/Atom}content')
        self.assertEquals(entries[0].text.strip(), u'I am good to go Canada')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9 Canada')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(
            entries[3].text.strip(), u'U+201C U+201D: \u201c\u201d')
        self.assertEquals(
            entries[4].text.strip(), u'U+2039 U+203A: \u2039\u203a')



pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

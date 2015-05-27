import unittest
import sys
import _mysql
import logging
from bottle import Bottle, request

from os.path import abspath, dirname
from ConfigParser import ConfigParser

sys.path.append(dirname(dirname(abspath(__file__))))

from webapp.webapp import WebApp
import pkppln


class TestPkpPln(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.handle = pkppln.get_connection()

    @classmethod
    def tearDownClass(self):
        pkppln.db_execute('TRUNCATE TABLE terms_of_use', db=self.handle)
        self.handle.commit()

    def setUp(self):
        pkppln.db_execute('TRUNCATE TABLE terms_of_use', db=self.handle)
        sql = """
INSERT INTO terms_of_use (weight, key_code, lang_code, content) 
VALUES (%s, %s, %s, %s)
"""
        data = [
            (0, 'utf8.single', 'en-US', u'I am good to go.'),
            (1, 'utf8.double', 'en-US', u'U+00E9: \u00E9'),
            (2, 'utf8.triple', 'en-US', u'U+20AC: \u20AC'),
            (3, 'typographic.doublequote', 'en-US',
             u'U+201C U+201D: \u201C \u201D'),
            (4, 'single.anglequote', 'en-US', u'U+2039 U+203A: \u2039 \u203A'),
            (0, 'utf8.single', 'en-CA', u'I am good to go Canada'),
            (1, 'utf8.double', 'en-CA', u'U+00E9: \u00E9 Canada'),
        ]
        self.handle.cursor().executemany(sql, data)
        self.handle.commit()

    def test_get_request_lang(self):
        application = WebApp('testapp')
        lang = application.get_request_lang('da, en-gb;q=0.8, en;q=0.7')
        self.assertEquals('en-US', lang)
        lang = application.get_request_lang('en, en-gb;q=0.8, en-CA;q=0.7')
        self.assertEquals('en-CA', lang)
        lang = application.get_request_lang('en, en-CA;q=0.8, en-US;q=0.7')
        self.assertEquals('en-CA', lang)
        lang = application.get_request_lang(None)
        self.assertEquals('en-US', lang)


# -----------------------------------------------------------------------------


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

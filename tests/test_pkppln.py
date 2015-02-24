import unittest
import sys
import _mysql
import logging

from os.path import abspath, dirname
from ConfigParser import ConfigParser

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase


class TestPkpPln(PkpPlnTestCase):

    # -----------------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        super(TestPkpPln, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestPkpPln, cls).tearDownClass()

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

    def tearDown(self):
        pkppln.db_execute('TRUNCATE TABLE terms_of_use', db=self.handle)
        self.handle.commit()

# -----------------------------------------------------------------------------

    def test_config(self):
        config = pkppln.get_config()
        self.assertIsInstance(config, ConfigParser)
        self.assertNotEqual(None, config.get('Database', 'db_name'))

# -----------------------------------------------------------------------------

    def test_connection(self):
        handle = pkppln.get_connection()
        self.assertIsInstance(handle, _mysql.connection)

# -----------------------------------------------------------------------------

    def test_logger(self):
        logger = pkppln.get_logger()
        self.assertIsInstance(logger, logging.Logger)


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

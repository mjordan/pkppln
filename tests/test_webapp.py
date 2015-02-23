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

    def test_get_request_lang(self):
        app = WebApp('testapp')
        lang = app.get_request_lang('da, en-gb;q=0.8, en;q=0.7')
        self.assertEquals('en-US', lang)
        lang = app.get_request_lang('en, en-gb;q=0.8, en-CA;q=0.7')
        self.assertEquals('en-CA', lang)
        lang = app.get_request_lang('en, en-CA;q=0.8, en-US;q=0.7')
        self.assertEquals('en-CA', lang)
        lang = app.get_request_lang(None)
        self.assertEquals('en-US', lang)


# -----------------------------------------------------------------------------


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

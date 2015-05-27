import unittest
import sys
from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
from tests.pln_testcase import PkpPlnTestCase
from webapp.feeds.feed_server import FeedsApp
import pkppln


class TestProcessing(PkpPlnTestCase):
    @classmethod
    def setUpClass(self):
        super(TestProcessing, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        # super(TestProcessing, self).tearDownClass()
        pass

    def test_basics(self):
        self.assertTrue(True)


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

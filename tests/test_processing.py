import string
import unittest
from argparse import Namespace
import sys
from os.path import abspath, dirname

# must be at the front of the path.
sys.path.insert(0, dirname(dirname(abspath(__file__))))
from commands.microcommands.list_services import ListServices
from tests.pln_testcase import PkpPlnTestCase
import pkppln


class TestProcessing(PkpPlnTestCase):

    @classmethod
    def setUpClass(self):
        super(TestProcessing, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(TestProcessing, self).tearDownClass()

    def test_processing(self):
        args = Namespace(verbose=1, force=False,
                         dry_run=False, config='config_test.cfg')
        for microtest in ListServices(args).services():
            test_module = 'tests.functional.' + microtest
            module = __import__(test_module, fromlist=[microtest])
            classname = string.capwords(microtest, '_').replace('_', '') + 'TestCase'
            module_class = getattr(module, classname)

            test_object = module_class()
            setUp = getattr(test_object, 'setUpClass')
            setUp()
            test_object.runTest()
            tearDown = getattr(test_object, 'tearDownClass')
            tearDown()
            return

pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

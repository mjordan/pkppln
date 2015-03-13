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
        path = dirname(abspath(__file__)) + '/functional'
        for service in ListServices(args).services():
            try:
                tm = 'tests.functional.' + service
                module = __import__(tm, fromlist=[service])
                class_name = string.capwords(service, '_').replace('_', '') + 'TestCase'
                module_class = getattr(module, class_name)
                test_obj = module_class()
                test_obj.__init__()
            # test gets run automatically.
            except Exception as e:
                print e


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

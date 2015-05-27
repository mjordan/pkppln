import unittest
import sys
from os.path import abspath, dirname
from argparse import Namespace

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.processing_testcase import ProcessingTestCase
from services.microservices.reserialize_bag import ReserializeBag

base_path = dirname(dirname(dirname(abspath(__file__))))


class ReserializeBagTestCase(ProcessingTestCase):

    @classmethod
    def setUpClass(self):
        super(ReserializeBagTestCase, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(ReserializeBagTestCase, self).tearDownClass()

    def runTest(self):
        self.test_virus_check()

    def test_virus_check(self):
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
            db=self.handle
        )[0]
        args = Namespace(verbose=1, force=False, 
                         dry_run=False, config='config_test.cfg')
        cmd = ReserializeBag(args)
        cmd.process_deposit(deposit)

        # don't use db=self.handle here. It returns the cached
        # deposit. Let pkppln get a new db connection instead.
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
        )[0]

        self.assertEquals('reserialized', deposit['processing_state'])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

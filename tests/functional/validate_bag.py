import unittest
import sys
from os.path import abspath, dirname
from argparse import Namespace

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.processing_testcase import ProcessingTestCase
from services.microservices.validate_bag import ValidateBag

base_path = dirname(dirname(dirname(abspath(__file__))))


class ValidateBagTestCase(ProcessingTestCase):

    @classmethod
    def setUpClass(self):
        super(ValidateBagTestCase, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(ValidateBagTestCase, self).tearDownClass()

    def runTest(self):
        self.test_validate_bag()

    def test_validate_bag(self):
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
            db=self.handle
        )[0]
        args = Namespace(verbose=1, force=False,
                         dry_run=False, config='config_test.cfg')
        cmd = ValidateBag(args)
        cmd.process_deposit(deposit)

        # don't use db=self.handle here. It returns the cached
        # deposit. Let pkppln get a new db connection instead.
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
        )[0]
        cmd.process_messages()
        self.assertEquals('bagValidated', deposit['processing_state'])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

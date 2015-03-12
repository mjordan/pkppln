
import unittest
import sys
from os.path import abspath, dirname
import os.path
from argparse import Namespace

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase
from services.microservices.validate_payload import ValidatePayload


class ValidatePayloadTest(PkpPlnTestCase):

    @classmethod
    def setUpClass(self):
        super(ValidatePayloadTest, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(ValidatePayloadTest, self).tearDownClass()

    def test_validate_payload(self):
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
            db=self.handle
        )[0]

        deposit['processing_state'] = 'harvested'
        args = Namespace(verbose=1, force=False, 
                         dry_run=False, config='config_test.cfg')
        cmd = ValidatePayload(args)

        try:
            cmd.process_deposit(deposit)
        except Exception as e:
            self.fail(e.message)
            return

        # don't use db=self.handle here. It returns the cached
        # deposit. Let pkppln get a new db connection instead.
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
        )[0]
        self.assertEquals('payloadVerified', deposit['processing_state'])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

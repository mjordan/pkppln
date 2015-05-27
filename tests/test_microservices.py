import traceback
import unittest
import sys
from os.path import abspath, dirname
from lxml import etree as ET
from argparse import Namespace
import string

sys.path.append(dirname(abspath(__file__)))
sys.path.append(dirname(dirname(abspath(__file__))))
from tests.pln_testcase import PkpPlnTestCase
import pkppln

parser = ET.XMLParser()


class TestMicroservices(PkpPlnTestCase):

    @classmethod
    def setUpClass(self):
        super(TestMicroservices, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(TestMicroservices, self).tearDownClass()

    def test_services(self):
        args = Namespace(
            verbose=2,
            force=False,
            dry_run=False,
            config='config_test.cfg',
            deposit='C7DD3B7D-8AD5-445A-89C1-EFB7CCBD4466'
        )

        services = [
            'harvest',
            'validate_payload',
            'validate_bag',
            'virus_check',
            'validate_export',
            'reserialize_bag',
            'stage_bag',
            'deposit_to_pln',
            'check_status'
        ]

        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
        )[0]

        base_path = dirname(dirname(abspath(__file__)))
        deposit['deposit_url'] = 'file://' + base_path + \
            '/tests/data/C7DD3B7D-8AD5-445A-89C1-EFB7CCBD4466'

        for service in services:
            print service
            if service in ['validate_export', 'deposit_to_pln']:
                continue

            module_name = 'services.microservices.' + service
            module = __import__(module_name, fromlist=[service])
            class_name = string.capwords(service, '_').replace('_', '')
            module_class = getattr(module, class_name)
            args.__setattr__('service', service)
            service_object = module_class(args)
            try:
                service_object.execute(deposit)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                self.fail(e)


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

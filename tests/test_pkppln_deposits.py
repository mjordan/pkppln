import unittest
import sys

from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase


class TestPkpPlnDeposits(PkpPlnTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPkpPlnDeposits, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestPkpPlnDeposits, cls).tearDownClass()

    def test_get_journal_deposits(self):
        deposits = pkppln.get_journal_deposits(2)
        self.assertEquals(1, len(deposits))
        self.assertEquals(
            'EF4D683B-A6DC-E0B6-F454-9E0A7E75F302',
            deposits[0]['deposit_uuid']
        )

    def test_get_deposit(self):
        deposit = pkppln.get_deposit('E89B7617-3201-9D24-51F2-5B46592C6A35')[0]
        self.assertIsNotNone(deposit)
        self.assertEquals(
            'E89B7617-3201-9D24-51F2-5B46592C6A35',
            deposit['deposit_uuid']
        )
        deposit = pkppln.get_deposit('zzz')
        self.assertIsNone(deposit)

    def test_get_deposits(self):
        deposits = pkppln.get_deposits('deposited')
        self.assertEquals(3, len(deposits))

    def test_update_deposit(self):
        pkppln.update_deposit('E89B7617-3201-9D24-51F2-5B46592C6A35', 'testing',
                              'tested', db=self.handle)
        deposit = pkppln.get_deposit('E89B7617-3201-9D24-51F2-5B46592C6A35',
                                     db=self.handle)[0]
        self.assertEquals('testing', deposit['processing_state'])
        self.assertEquals('tested', deposit['outcome'])
        self.handle.rollback()

    def test_update_deposit_exception(self):
        raised = False
        try:
            pkppln.update_deposit('E89B7617-3201-9D24-51F2-5B46592C6A35', None,
                                  'tested', db=self.handle)[0]
        except:
            raised = True
        self.assertTrue(raised, 'Exception raised')
        self.handle.rollback()

    def test_insert_deposit(self):
        pkppln.insert_deposit(
            '9a6e5ad9-f783-4166-9e28-6dffc5de83cb',
            '8e99d97e-43f0-49ca-97dd-2075c8ef784f',
            1,
            'add',
            '4',
            '5',
            '2015-02-17',
            '5c9b43b12a427a8a058992bbbfbbed86b63a2870',
            'http://ojs.example.com/ijt/pln/deposits/9a6e5ad9-f783-4166-9e28-6dffc5de83cb',
            3612,
            'depositedByJournal',
            'success',
            db=self.handle
        )
        self.handle.commit()
        deposit = pkppln.get_deposit('9a6e5ad9-f783-4166-9e28-6dffc5de83cb')[0]
        self.assertIsNotNone(deposit)
        self.assertEquals('depositedByJournal', deposit['processing_state'])

    def test_insert_deposit_exception(self):
        raised = False
        try:
            pkppln.insert_deposit(
                '9a6e5ad9-f783-4166-9e28-6dffc5de83cb',
                '8e99d97e-43f0-49ca-97dd-2075c8ef784f',
                1,
                None,
                '4',
                '5',
                '2015-02-17',
                '5c9b43b12a427a8a058992bbbfbbed86b63a2870',
                'http://ojs.example.com/ijt/pln/deposits/9a6e5ad9-f783-4166-9e28-6dffc5de83cb',
                3612,
                'depositedByJournal',
                'success',
                db=self.handle
            )
        except:
            raised = True
        self.assertTrue(raised)
        self.handle.commit()
        deposit = pkppln.get_deposit('9a6e5ad9-f783-4166-9e28-6dffc5de83cb')
        self.assertIsNone(deposit)


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

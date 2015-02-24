import unittest
import sys
import _mysql
import logging

from os.path import abspath, dirname
from ConfigParser import ConfigParser

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln


class TestPkpPln(unittest.TestCase):

    # -----------------------------------------------------------------------------

    @classmethod
    def setUpClass(self):
        self.handle = pkppln.get_connection()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pkppln.db_execute('DELETE FROM microservices', db=self.handle)
        pkppln.db_execute('ALTER TABLE microservices AUTO_INCREMENT=1',
                          db=self.handle)
        pkppln.db_execute('DELETE FROM deposits', db=self.handle)
        pkppln.db_execute('DELETE FROM journals', db=self.handle)
        sql = """
INSERT INTO journals (journal_uuid, title, issn,
journal_url, journal_status, contact_email, publisher_name, publisher_url)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = [
            (
                '7D3C4239-2A73-29F4-B34D-ABFD53EA147D',
                'Intl J Test',
                '9876-5432',
                'http://ojs1.example.com/index.php/ijt',
                'healthy',
                'ijt@example.com',
                'Publisher institution',
                'http://publisher.example.com'
            ), (
                '8e99d97e-43f0-49ca-97dd-2075c8ef784f',
                'J Intl Fun',
                '7777-7777',
                'http://ojs.example.com/jiffy',
                'healthy',
                'jiffy@example.com',
                'Fun Inst',
                'http://fun.example.com'
            )
        ]
        self.handle.cursor().executemany(sql, data)

        sql = """
INSERT INTO deposits (deposit_uuid, journal_uuid, date_deposited, 
deposit_action, deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1, 
deposit_url, deposit_size, processing_state, outcome, pln_state, deposited_lom, 
deposit_receipt)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        data = [
            (
                '61AEF065-71DE-93AA-02B0-5618ABAC2393',
                '7D3C4239-2A73-29F4-B34D-ABFD53EA147D',
                '2015-02-17 19:47:37',
                'add',
                '44',
                '3',
                '2015-02-17',
                '6c1d6114e6fd0e2562f93621bba1602278df5a74',
                'http://ojs.dev/index.php/ijt/pln/deposits/61AEF065-71DE-93AA-02B0-5618ABAC2393',
                1299,
                'deposited',
                'success',
                'inProgress',
                '2015-02-20 21:30:41',
                'http://lom.dev/web/app_dev.php/api/sword/2.0/cont-iri/7D3C4239-2A73-29F4-B34D-ABFD53EA147D/61AEF065-71DE-93AA-02B0-5618ABAC2393/edit'
            ),
            (
                '9CDBA9E6-9C04-74DC-4A80-D6972C1A10D0',
                '7D3C4239-2A73-29F4-B34D-ABFD53EA147D',
                '2015-02-17 19:47:39',
                'add',
                '1',
                '1',
                '2015-02-17',
                '42b96cab4fe4a18405307464651a10c86b850fa5',
                'http://ojs.dev/index.php/ijt/pln/deposits/9CDBA9E6-9C04-74DC-4A80-D6972C1A10D0',
                8882,
                'deposited',
                'success',
                'inProgress',
                '2015-02-20 21:30:41',
                'http://lom.dev/web/app_dev.php/api/sword/2.0/cont-iri/7D3C4239-2A73-29F4-B34D-ABFD53EA147D/9CDBA9E6-9C04-74DC-4A80-D6972C1A10D0/edit'),
            (
                'E89B7617-3201-9D24-51F2-5B46592C6A35',
                '7D3C4239-2A73-29F4-B34D-ABFD53EA147D',
                '2015-02-17 19:47:41', 'add',
                '1',
                '1',
                '2015-02-17',
                '7ac3a61d321b1ca06fe50e44eae061411a2c9267',
                'http://ojs.dev/index.php/ijt/pln/deposits/E89B7617-3201-9D24-51F2-5B46592C6A35',
                8882,
                'virusChecked',
                'success',
                'inProgress',
                '0000-00-00 00:00:00',
                'http://lom.dev/web/app_dev.php/api/sword/2.0/cont-iri/7D3C4239-2A73-29F4-B34D-ABFD53EA147D/E89B7617-3201-9D24-51F2-5B46592C6A35/edit'
            ),
            (
                'EF4D683B-A6DC-E0B6-F454-9E0A7E75F302',
                '8e99d97e-43f0-49ca-97dd-2075c8ef784f',
                '2015-02-17 19:47:35',
                'add',
                '44',
                '4',
                '2015-02-17',
                '5c9b43b12a427a8a058992bbbfbbed86b63a2870',
                'http://ojs.dev/index.php/ijt/pln/deposits/EF4D683B-A6DC-E0B6-F454-9E0A7E75F302',
                3612,
                'deposited',
                'success',
                'inProgress',
                '2015-02-20 21:30:41',
                'http://lom.dev/web/app_dev.php/api/sword/2.0/cont-iri/7D3C4239-2A73-29F4-B34D-ABFD53EA147D/EF4D683B-A6DC-E0B6-F454-9E0A7E75F302/edit'
            ),
        ]
        self.handle.cursor().executemany(sql, data)

        self.handle.commit()

    def tearDown(self):
        pkppln.db_execute('DELETE FROM microservices', db=self.handle)
        pkppln.db_execute(
            'ALTER TABLE microservices AUTO_INCREMENT=1', db=self.handle)
        pkppln.db_execute('DELETE FROM deposits', db=self.handle)
        pkppln.db_execute('DELETE FROM journals', db=self.handle)
        self.handle.commit()

# -----------------------------------------------------------------------------

    def test_get_journal_deposits(self):
        deposits = pkppln.get_journal_deposits(
            '8e99d97e-43f0-49ca-97dd-2075c8ef784f'
        )
        self.assertEquals(1, len(deposits))
        self.assertEquals(
            'EF4D683B-A6DC-E0B6-F454-9E0A7E75F302',
            deposits[0]['deposit_uuid']
        )

    def test_get_deposit(self):
        deposit = pkppln.get_deposit('E89B7617-3201-9D24-51F2-5B46592C6A35')
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
                                     db=self.handle)
        self.assertEquals('testing', deposit['processing_state'])
        self.assertEquals('tested', deposit['outcome'])
        self.handle.rollback()

    def test_update_deposit_exception(self):
        raised = False
        try:
            pkppln.update_deposit('E89B7617-3201-9D24-51F2-5B46592C6A35', None,
                                  'tested', db=self.handle)
        except:
            raised = True
        self.assertTrue(raised)
        self.handle.rollback()

    def test_insert_deposit(self):
        pkppln.insert_deposit(
            '9a6e5ad9-f783-4166-9e28-6dffc5de83cb',
            '8e99d97e-43f0-49ca-97dd-2075c8ef784f',
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
        deposit = pkppln.get_deposit('9a6e5ad9-f783-4166-9e28-6dffc5de83cb')
        self.assertIsNotNone(deposit)
        self.assertEquals('depositedByJournal', deposit['processing_state'])

    def test_insert_deposit_exception(self):
        raised = False
        try:
            pkppln.insert_deposit(
                '9a6e5ad9-f783-4166-9e28-6dffc5de83cb',
                '8e99d97e-43f0-49ca-97dd-2075c8ef784f',
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

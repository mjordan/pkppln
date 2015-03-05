import unittest
import sys
from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln


class PkpPlnTestCase(unittest.TestCase):

    @classmethod
    def clear_database(cls):
        pkppln.db_execute(
            'DELETE FROM microservices',
            db=cls.handle
        )
        pkppln.db_execute(
            'ALTER TABLE microservices AUTO_INCREMENT=1',
            db=cls.handle
        )
        pkppln.db_execute(
            'DELETE FROM deposits',
            db=cls.handle
        )
        pkppln.db_execute(
            'ALTER TABLE deposits AUTO_INCREMENT=1',
            db=cls.handle
        )
        pkppln.db_execute(
            'DELETE FROM journals',
            db=cls.handle
        )
        pkppln.db_execute(
            'ALTER TABLE journals AUTO_INCREMENT=1',
            db=cls.handle
        )
        pkppln.db_execute(
            'TRUNCATE TABLE terms_of_use',
            db=cls.handle
        )
        cls.handle.commit()

    @classmethod
    def setUpClass(cls):
        cls.handle = pkppln.get_connection()
        cls.clear_database()

    @classmethod
    def tearDownClass(cls):
        cls.clear_database()

    def setUp(self):
        self.clear_database()
        sql = """
INSERT INTO terms_of_use (weight, key_code, lang_code, content)
VALUES (%s, %s, %s, %s)
"""
        data = [
            (0, 'utf8.single', 'en-US', u'I am good to go.'),
            (1, 'utf8.double', 'en-US', u'U+00E9: \u00E9'),
            (2, 'utf8.triple', 'en-US', u'U+20AC: \u20AC'),
            (3, 'typographic.doublequote', 'en-US',
             u'U+201C U+201D: \u201C \u201D'),
            (4, 'single.anglequote', 'en-US', u'U+2039 U+203A: \u2039 \u203A'),
            (0, 'utf8.single', 'en-CA', u'I am good to go Canada'),
            (1, 'utf8.double', 'en-CA', u'U+00E9: \u00E9 Canada'),
        ]
        self.handle.cursor().executemany(sql, data)
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
INSERT INTO deposits (deposit_uuid, file_uuid, journal_id, date_deposited, 
deposit_action, deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1, 
deposit_url, deposit_size, processing_state, outcome, pln_state, deposited_lom, 
deposit_receipt)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        data = [
            (
                '61AEF065-71DE-93AA-02B0-5618ABAC2393',
                'C7DD3B7D-8AD5-445A-89C1-EFB7CCBD4466',
                1,
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
                '86800F0E-C558-40EE-9A92-1537E405C259',
                1,
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
                '1631D575-0D7F-4D4C-B38D-8153273FE55E',
                1,
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
                '797863CA-428F-485A-82B4-0DC584663B8A',
                2,
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

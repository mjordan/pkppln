import unittest
from os.path import abspath, dirname
import sys
from collections import namedtuple

sys.path.remove(dirname(abspath(__file__)))
sys.path.insert(1, dirname(dirname(dirname(dirname(abspath(__file__))))))
from commands.microcommands.journal_info import JournalInfo
import pkppln


class TestJournalInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestJournalInfo, cls).setUpClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.executemany(
            """INSERT INTO journals(journal_uuid, title, issn, journal_url,
                   contact_email, deposit_uuid, date_deposited)
               VALUES(%s, %s, %s, %s, %s, %s, %s)
           """,
            [
                (
                    'BBB187B8-61B2-BB38-86E2-C43902816AE8', 'Intl J Test',
                    '9876-5432', 'http://ojs.dev/index.php/ijt',
                    'test@example.com', 'BA7C44C8-91E5-D61E-8409-DDFC230EBF33',
                    '2014-12-01 10:35:16'
                ),
                (
                    'BBB187B8-61B2-BB38-86E2-C43902816AE8', 'Intl J Test',
                    '9876-5432', 'http://ojs.dev/index.php/ijt',
                    'test@example.com', '315E8280-CD2D-1038-3D83-415E68DBF2E0',
                    '2014-12-01 10:35:16'
                ),
                (
                    'BBB187B8-61B2-BB38-86E2-C43902816AE8', 'Intl J Testing',
                    '9876-5432', 'http://ojs.dev/index.php/ijt',
                    'test@example.com', '90F96C60-9989-506A-85B3-052ADEDC4831',
                    '2014-12-01 10:35:16'
                ),
                (
                    'BBB187B8-61B2-BB38-86E2-C43902816AE8', 'Intl J Testing',
                    '9876-5432', 'http://ojs.dev/index.php/ijt',
                    'test@example.com', 'D924C1EC-C38C-3FD4-2553-888758EA8FEA',
                    '2014-12-01 10:35:16'
                ),
            ]
        )
        mysql.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestJournalInfo, cls).tearDownClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM journals')
        mysql.commit()

    def testJournalUUID(self):
        cmd = JournalInfo()
        argsdict = {'uuid': 'BBB187B8-61B2-BB38-86E2-C43902816AE8'}
        args = namedtuple('args', argsdict.keys())(**argsdict)
        output = cmd.execute(args)
        # header, four entries, blank line.
        self.assertEquals(3, len(output.split('\n\n')))
        self.assertEquals(2, output.count('9876-5432'))
        self.assertEquals(1, output.count('Intl J Test\n'))
        self.assertEquals(1, output.count('Intl J Testing'))

    def testDepositUUID(self):
        cmd = JournalInfo()
        argsdict = {'uuid': 'D924C1EC-C38C-3FD4-2553-888758EA8FEA'}
        args = namedtuple('args', argsdict.keys())(**argsdict)
        output = cmd.execute(args)
        # header, four entries, blank line.
        self.assertEquals(3, len(output.split('\n\n')))
        self.assertEquals(2, output.count('9876-5432'))
        self.assertEquals(1, output.count('Intl J Test\n'))
        self.assertEquals(1, output.count('Intl J Testing'))


if __name__ == '__main__':  # pragma: no cover
    pkppln.config_file_name = 'config_test.cfg'
    unittest.main()

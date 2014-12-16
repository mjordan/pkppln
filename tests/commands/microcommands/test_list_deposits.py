import unittest
from os.path import abspath, dirname
import sys
from collections import namedtuple

sys.path.remove(dirname(abspath(__file__)))
sys.path.insert(1, dirname(dirname(dirname(dirname(abspath(__file__))))))
from commands.microcommands.list_deposits import ListDeposits
import pkppln


class TestListDeposits(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestListDeposits, cls).setUpClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        sys.exit('NOT FINISHED YET.')
        cursor.executemany(
            """INSERT INTO deposits (action, deposit_uuid, deposit_volume,
                        deposit_issue, deposit_pubdate, date_deposited,
                        journal_uuid, sha1_value, deposit_url, size,
                        processing_state, outcome, pln_state, deposited_lom)
               VALUES()
            """,
            [
            ]
        )
        mysql.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestListDeposits, cls).tearDownClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM microservices')
        mysql.commit()

    def testListDeposits(self):
        cmd = ListDeposits()
        argsdict = {'deposit': 'BA7C44C8-91E5-D61E-8409-DDFC230EBF33'}
        args = namedtuple('args', argsdict.keys())(**argsdict)
        output = cmd.execute(args)
        # header, four content lines, blank line.
        self.assertEquals(6, len(output.split('\n')))
        self.assertEquals(3, output.count('success'))
        self.assertEquals(1, output.count('failed'))

pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

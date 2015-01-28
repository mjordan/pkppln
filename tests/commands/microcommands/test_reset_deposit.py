import unittest
from os.path import abspath, dirname
import sys
from collections import namedtuple

sys.path.remove(dirname(abspath(__file__)))
sys.path.insert(1, dirname(dirname(dirname(dirname(abspath(__file__))))))
from commands.microcommands.reset_deposit import ResetDeposit
import pkppln


class TestResetDeposit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestResetDeposit, cls).setUpClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.executemany("""
            INSERT INTO deposits (action, deposit_uuid, deposit_volume,
                deposit_issue, deposit_pubdate, date_deposited, journal_uuid,
                sha1_value, deposit_url, size, processing_state, outcome,
                pln_state)
            VALUES ('add', %s, 44, %s, '2014-12-15', '2014-12-16',
                'BBB187B8-61B2-BB38-86E2-C43902816AE8', %s, %s,
                1024, %s, %s, 'in_progress')
        """, [
            (
                'BA7C44C8-91E5-D61E-8409-DDFC230EBF33', '1',
                '4bf1ecc03abdea30b3263a905d74d798b1bfddc6',
                'http://ojs.dev/index.php/ijt/pln/deposits/BA7C44C8-91E5-D61E-8409-DDFC230EBF33',
                'deposited',
                'success'
            ),
            (
                '315E8280-CD2D-1038-3D83-415E68DBF2E0', '2',
                'fc9e099dc0d66fb8945db0e6d7e1e2e201e9c790',
                'http://ojs.dev/index.php/ijt/pln/deposits/315E8280-CD2D-1038-3D83-415E68DBF2E0',
                'deposited',
                'failed'
            ),
            (
                '90F96C60-9989-506A-85B3-052ADEDC4831', '3',
                'fc9e099dc0d66fb8945db0e6d7e1e2e201e9c790',
                'http://ojs.dev/index.php/ijt/pln/deposits/90F96C60-9989-506A-85B3-052ADEDC4831',
                'harvested',
                'success'
            )
        ]
        )
        mysql.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestResetDeposit, cls).tearDownClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM deposits')
        mysql.commit()

    def testResetDeposit(self):
        cmd = ResetDeposit()
        argsdict = {
            'uuid': '90F96C60-9989-506A-85B3-052ADEDC4831',
            'state': 'deposited'
        }
        args = namedtuple('args', argsdict.keys())(**argsdict)
        output = cmd.execute(args)
        # header, four entries, blank line.
        self.assertEquals('', output)
        deposit = pkppln.get_deposit('90F96C60-9989-506A-85B3-052ADEDC4831')
        self.assertEquals('deposited', deposit['processing_state'])
        self.assertEquals('reset', deposit['outcome'])
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute("""
            SELECT * FROM microservices
            WHERE deposit_uuid = %s
            ORDER BY id DESC 
            LIMIT 1;""", ['90F96C60-9989-506A-85B3-052ADEDC4831'])
        msl = cursor.fetchone()
        self.assertEquals('deposited', msl['microservice'])
        self.assertEquals('reset', msl['outcome'])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

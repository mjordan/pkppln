import unittest
from os.path import abspath, dirname
import sys
from collections import namedtuple

sys.path.remove(dirname(abspath(__file__)))
sys.path.insert(1, dirname(dirname(dirname(dirname(abspath(__file__))))))
from commands.microcommands.service_log import ServiceLog
import pkppln


class TestServiceLog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestServiceLog, cls).setUpClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.executemany(
            """INSERT INTO microservices (microservice, deposit_uuid,
                            started_on, finished_on, outcome, error)
               VALUES(%s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    'Harvest', 'BA7C44C8-91E5-D61E-8409-DDFC230EBF33',
                    '2014-12-10 10:00:00', '2014-12-10 10:35:16', 'success',
                    ''
                ),
                (
                    'validatePayload', 'BA7C44C8-91E5-D61E-8409-DDFC230EBF33',
                    '2014-12-10 10:00:00', '2014-12-10 10:35:16', 'success',
                    ''
                ),
                (
                    'validateBag', 'BA7C44C8-91E5-D61E-8409-DDFC230EBF33',
                    '2014-12-10 10:00:00', '2014-12-10 10:35:16', 'success',
                    ''
                ),
                (
                    'virusCheck', 'BA7C44C8-91E5-D61E-8409-DDFC230EBF33',
                    '2014-12-10 10:00:00', '2014-12-10 10:35:16', 'failed',
                    ''
                ),
                (
                    'Harvest', 'ABCABCAB-91E5-D61E-8409-DDFC230EBF33',
                    '2014-12-10 10:00:00', '2014-12-10 10:35:16', 'success',
                    ''
                ),
            ]
        )
        mysql.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestServiceLog, cls).tearDownClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM microservices')
        mysql.commit()

    def testServiceLog(self):
        cmd = ServiceLog()
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

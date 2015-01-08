import unittest
from os.path import abspath, dirname
import sys

sys.path.remove(dirname(abspath(__file__)))
sys.path.insert(1, dirname(dirname(dirname(dirname(abspath(__file__))))))
from services.microservices.harvest import Harvest
import pkppln


class TestListDeposits(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestListDeposits, cls).setUpClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.executemany("""""", [])
        mysql.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestListDeposits, cls).tearDownClass()
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM deposits')
        mysql.commit()

    def testHarvest(self):
        service = Harvest()
        deposit = {
            'deposit_uuid': '402a6e97-dbd2-4aba-a3e4-234aabb4314c',
            'deposit_url': 'http://localhost:8080/deposits/testing/402a6e97-dbd2-4aba-a3e4-234aabb4314c'
        }
        result = service.execute(deposit)
        self.assertEquals('success', result[0])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

import unittest
import sys
import _mysql
import logging

from os.path import abspath, dirname
from ConfigParser import ConfigParser

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln


class TestPkpPln(unittest.TestCase):

    """Tests for the pkppln lib."""

    def setUp(self):
        unittest.TestCase.setUp(self)
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            """INSERT INTO `deposits` (`id`, `action`, `deposit_uuid`,
            `deposit_volume`, `deposit_issue`, `deposit_pubdate`,
            `date_deposited`, `journal_uuid`, `sha1_value`, `deposit_url`,
            `size`, `processing_state`, `outcome`, `pln_state`,
            `deposited_lom`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s)
            """,
            ['1', 'add', '1234', '4', '5', '2010-12-25', '2011-01-01', '456',
             '123', 'http://example.com/jrnl/foo.zip', '1023',
             'depositedByJournal', 'success', 'in_progress', '0000-00-00'
             ]
        )
        cursor.execute("""INSERT INTO `journals` (`id`, `journal_uuid`,
        `title`, `issn`, `journal_url`, `contact_email`, `deposit_uuid`,
        `date_deposited`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""",
                       ['1', '456', 'IJTesting', '123456',
                        'http://example.com', 'example@example.com', '1234',
                        '2010-12-25'])
        mysql.commit()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute('DELETE FROM journals')
        cursor.execute('DELETE FROM deposits')
        cursor.execute('DELETE FROM microservices')
        cursor.execute('DELETE FROM terms_of_use')
        mysql.commit()

    def test_config(self):
        config = pkppln.get_config()
        self.assertIsInstance(config, ConfigParser)
        self.assertEquals('pkpplntest', config.get('Database', 'db_name'))

    def test_connection(self):
        mysql = pkppln.get_connection()
        self.assertIsInstance(mysql, _mysql.connection)

    def test_logger(self):
        logger = pkppln.get_logger()
        self.assertIsInstance(logger, logging.Logger)

    def test_check_access(self):
        config = pkppln.get_config()
        config.set('Deposits', 'pln_accept_deposits', 'No')
        self.assertEquals('No', pkppln.check_access('1123'))

        config.set('Deposits', 'pln_accept_deposits', 'Yes')
        self.assertEquals('Yes', pkppln.check_access('1123'))

    def test_get_deposits(self):
        deposits = pkppln.get_deposits('depositedByJournal')
        self.assertEquals(1, len(deposits))
        deposits = pkppln.get_deposits('harvested')
        self.assertEquals(0, len(deposits))
        pass

    def test_update_deposit(self):
        pass

    def test_insert_deposit(self):
        pass

    def test_insert_journal(self):
        pass

    def test_get_journal(self):
        pass

    def test_get_journal_xml(self):
        pass

    def test_deposit_filename(self):
        pass

    def test_file_sha1(self):
        pass

    def test_file_md5(self):
        pass

    def test_input_path(self):
        pass

    def test_microservice_directory(self):
        pass


if __name__ == '__main__':
    pkppln.config_file_name = 'config_test.cfg'
    unittest.main()

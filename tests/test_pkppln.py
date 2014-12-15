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
        self.assertNotEqual(None, config.get('Database', 'db_name'))

    def test_connection(self):
        mysql = pkppln.get_connection()
        self.assertIsInstance(mysql, _mysql.connection)

    def test_logger(self):
        logger = pkppln.get_logger()
        self.assertIsInstance(logger, logging.Logger)

    def test_check_access(self):
        config = pkppln.get_config()

        # the whitelist config doesn't exist yet.
        self.assertEquals(
            'Yes',
            pkppln.check_access('083c76f3-d5be-4eae-8314-c58180039719')
        )

        config.set('Deposits', 'pln_accept_deposits_whitelist',
                   dirname(abspath(__file__)) + '/data/whitelist.txt')
        config.set('Deposits', 'pln_accept_deposits_blacklist',
                   dirname(abspath(__file__)) + '/data/blacklist.txt')

        config.set('Deposits', 'pln_accept_deposits', 'No')
        self.assertEquals('No', pkppln.check_access('1123'))

        config.set('Deposits', 'pln_accept_deposits', 'Yes')
        self.assertEquals(
            'Yes',
            pkppln.check_access('9109ba87-2816-4e7e-944b-c0d4f4587954'))
        # 357dc... is in the whitelist file, but it is commented out
        self.assertEquals(
            'No',
            pkppln.check_access('357dcf9e-24e3-4e8f-a6f8-3fbffa18e17c'))
        # 500e7... is blacklisted
        self.assertEquals(
            'No',
            pkppln.check_access('500e767a-133b-46b7-a3e9-f2d5ce1f52bc'))
        # 4e8a872a-5947-4ffb-b77a-da62e308cb5d is in neither file
        self.assertEquals(
            'No',
            pkppln.check_access('4e8a872a-5947-4ffb-b77a-da62e308cb5d'))

    def test_get_deposits(self):
        deposits = pkppln.get_deposits('depositedByJournal')
        self.assertEquals(1, len(deposits))
        deposits = pkppln.get_deposits('harvested')
        self.assertEquals(0, len(deposits))

    def test_update_deposit(self):
        deposits = pkppln.get_deposits('depositedByJournal')
        pkppln.update_deposit(deposits[0]['deposit_uuid'],
                              'harvested', 'success')
        deposits = pkppln.get_deposits('harvested')
        self.assertEquals(1, len(deposits))

    def test_insert_deposit(self):
        pkppln.insert_deposit('test', 'abc123', 1, 2, '2014-01-01', 'def432',
                              '21234a', 'http://example.com', 1124,
                              'depositTest', 'success')
        deposits = pkppln.get_deposits('depositTest')
        self.assertEquals(1, len(deposits))

    def test_get_journal(self):
        journal = pkppln.get_journal('1234')
        self.assertEquals('IJTesting', journal['title'])

    def test_insert_journal(self):
        pkppln.insert_journal('acbd', 'I J Test', '1234-5468',
                              'http://example.com/test', 'test@example.com',
                              'abcb3b3b2b4')
        journal = pkppln.get_journal('abcb3b3b2b4')
        self.assertEquals('I J Test', journal['title'])

    def test_get_journal_xml(self):
        xml = pkppln.get_journal_xml('1234')
        expected = """
        <pkp:root xmlns:pkp="http://pkp.sfu.ca/SWORD">
        <pkp:journal_uuid>456</pkp:journal_uuid>
        <pkp:title>IJTesting</pkp:title>
        <pkp:journal_url>http://example.com</pkp:journal_url>
        <pkp:issn>123456</pkp:issn>
        <pkp:date_deposited>2010-12-25</pkp:date_deposited>
        <pkp:contact_email>example@example.com</pkp:contact_email>
        <pkp:deposit_uuid>1234</pkp:deposit_uuid>
        <pkp:id>1</pkp:id></pkp:root>""".replace('\n        ', '')
        self.assertEquals(expected, xml)

    def test_deposit_filename(self):
        self.assertEquals('foo.tgz', pkppln.deposit_filename('//foo//foo.tgz'))

    def test_file_sha1(self):
        self.assertEquals(
            'e8f5474bfb88e48f503cad41ad2f39495abcf543',
            pkppln.file_sha1('tests/data/datafile'))

    def test_file_md5(self):
        self.assertEquals(
            'e34552303ce9c17d53f66689d883f63c',
            pkppln.file_md5('tests/data/datafile'))

    def test_input_path(self):
        self.assertEquals(
            '/var/mypln/a/',
            pkppln.input_path('a'))
        self.assertEquals(
            '/var/mypln/a/b/c/',
            pkppln.input_path('a', ['b', 'c']))
        self.assertEquals(
            '/var/mypln/a/b/c',
            pkppln.input_path('a', ['b'], 'c'))

    def test_microservice_directory(self):
        config = pkppln.get_config()
        # microservice_directory() will attempt to create the resulting dir.
        # so point it somewhere temporary.
        config.set('Paths', 'processing_root', '/tmp')
        self.assertEquals(
            '/tmp/test1/abc',
            pkppln.microservice_directory('test1', 'abc'))


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

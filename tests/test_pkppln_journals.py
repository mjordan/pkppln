import unittest
import sys
from lxml import etree as ET

from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln

parser = ET.XMLParser()


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
        self.handle.commit()

    def tearDown(self):
        pkppln.db_execute('DELETE FROM microservices', db=self.handle)
        pkppln.db_execute(
            'ALTER TABLE microservices AUTO_INCREMENT=1', db=self.handle)
        pkppln.db_execute('DELETE FROM deposits', db=self.handle)
        pkppln.db_execute('DELETE FROM journals', db=self.handle)
        self.handle.commit()

    def test_get_journal(self):
        jrnl = pkppln.get_journal('8e99d97e-43f0-49ca-97dd-2075c8ef784f')
        self.assertEqual('J Intl Fun', jrnl['title'])
        jrnl = pkppln.get_journal('zz')
        self.assertIsNone(jrnl)

    def test_insert_journal(self):
        pkppln.insert_journal('abc', 'Funsert', '1111-1111',
                              'http://funsert.example.com', 'fun@example.com',
                              'Publius', 'http://publius.example.com',
                              db=self.handle)
        jrnl = pkppln.get_journal('abc', db=self.handle)
        self.assertEquals('Funsert', jrnl['title'])
        self.handle.rollback()

    def test_insert_journal_exception(self):
        raised = False
        try:
            pkppln.insert_journal(None, 'Funsert', '1111-1111',
                                  'http://funsert.example.com', 'fun@example.com',
                                  'Publius', 'http://publius.example.com',
                                  db=self.handle)
        except:
            raised = True
        self.assertTrue(raised)
        self.handle.rollback()

    def test_get_journals(self):
        jrnls = pkppln.get_journals()
        self.assertEquals(2, len(jrnls))

    def test_get_journal_xml(self):
        xmlstr = pkppln.get_journal_xml('7D3C4239-2A73-29F4-B34D-ABFD53EA147D')
        root = ET.fromstring(xmlstr.encode('utf-8'))
        self.assertEquals(
            '7D3C4239-2A73-29F4-B34D-ABFD53EA147D',
            root.findall(
                './/{http://pkp.sfu.ca/SWORD}journal_uuid')[0].text
        )

pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

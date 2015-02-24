import unittest
import sys
from lxml import etree as ET

from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase


parser = ET.XMLParser()


class TestPkpPlnJournals(PkpPlnTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPkpPlnJournals, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestPkpPlnJournals, cls).tearDownClass()

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

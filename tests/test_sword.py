"""Tests for the Feeds module"""

import unittest
import sys
import xml.etree.ElementTree as ET
from os.path import abspath, dirname
from _elementtree import XMLParser
sys.path.append(dirname(dirname(abspath(__file__))))
import requests
import pkppln
from pkppln import namespaces, get_connection

with_server = False


class TestSwordServer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.handle = pkppln.get_connection()

    @classmethod
    def tearDownClass(self):
        pkppln.db_execute('DELETE FROM microservices', db=self.handle)
        pkppln.db_execute('ALTER TABLE microservices AUTO_INCREMENT=1',
                          db=self.handle)
        pkppln.db_execute('DELETE FROM deposits', db=self.handle)
        pkppln.db_execute('DELETE FROM journals', db=self.handle)
        pkppln.db_execute('TRUNCATE TABLE terms_of_use', db=self.handle)
        self.handle.commit()
        self.app = None

    def setUp(self):
        pkppln.db_execute('DELETE FROM microservices', db=self.handle)
        pkppln.db_execute('ALTER TABLE microservices AUTO_INCREMENT=1',
                          db=self.handle)
        pkppln.db_execute('DELETE FROM deposits', db=self.handle)
        pkppln.db_execute('DELETE FROM journals', db=self.handle)
        pkppln.db_execute('TRUNCATE TABLE terms_of_use', db=self.handle)
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
        self.handle.commit()

    def test_service_document(self):
        r = requests.get(
            'http://localhost:9999/api/sword/2.0/sd-iri',
            headers={
                'Journal-URL': 'http://jrnl.example.com',
                'On-Behalf-Of': 'b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9'
            }
        )
        self.assertEquals(200, r.status_code)
        self.assertEquals('UTF-8', r.encoding)
        root = ET.fromstring(r.content, parser=XMLParser(encoding='UTF-8'))
        entries = root.findall('.//{http://pkp.sfu.ca/SWORD}terms_of_use/*')
        self.assertEquals(entries[0].text.strip(), u'I am good to go.')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(
            entries[3].text.strip(), u'U+201C U+201D: \u201c \u201d')
        self.assertEquals(
            entries[4].text.strip(), u'U+2039 U+203A: \u2039 \u203a')

    def test_service_document_no_journal_url(self):
        r = requests.get(
            'http://localhost:9999/api/sword/2.0/sd-iri',
            headers={
                'On-Behalf-Of': 'b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9'
            }
        )
        self.assertEquals(400, r.status_code)
        self.assertEquals('UTF-8', r.encoding)

    def test_service_document_no_on_behalf(self):
        r = requests.get(
            'http://localhost:9999/api/sword/2.0/sd-iri',
            headers={
                'Journal-URL': 'http://jrnl.example.com',
            }
        )
        self.assertEquals(400, r.status_code)
        self.assertEquals('UTF-8', r.encoding)

    def test_create_deposit(self):
        deposit = """
 <entry xmlns="http://www.w3.org/2005/Atom"
        xmlns:dcterms="http://purl.org/dc/terms/"
        xmlns:pkp="http://pkp.sfu.ca/SWORD">
    <email>journal_manager@example.com</email>
    <title>Journal of Foo Studies</title>
    <pkp:issn>1234-123x</pkp:issn>
    <pkp:journal_url>http://jfs.example.org/index.php/jfs</pkp:journal_url>
    <pkp:publisherName>Publ Name</pkp:publisherName>
    <pkp:publisherUrl>http://pub.example.com</pkp:publisherUrl>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2013-10-07T17:17:08Z</updated>
    <pkp:content size="102400" checksumType="sha1" volume="4" issue="3" 
    pubdate = "2011-04-25" checksumValue="bd4a9b642562547754086de2dab26b7d">
        http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip
    </pkp:content>
</entry>
        """
        r = requests.post(
            'http://localhost:9999/api/sword/2.0/col-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9',
            data=deposit,
            headers={
                'Content-type': 'text/xml; charset=UTF-8'
            }
        )
        self.assertEquals(201, r.status_code)
        self.assertEquals('UTF-8', r.encoding)
        self.assertEquals(
            '/api/sword/2.0/cont-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            r.headers['location']
        )
        cursor = get_connection().cursor()
        cursor.execute('SELECT * FROM deposits')
        deposits = list(cursor.fetchall())
        self.assertEquals(1, len(deposits))
        self.assertEquals('1225c695-cfb8-4ebb-aaaa-80da344efa6a',
                          deposits[0]['deposit_uuid'])
        cursor.execute('SELECT * FROM journals')
        journals = list(cursor.fetchall())
        self.assertEquals(3, len(journals))
        jrnl = pkppln.get_journal('b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9')
        self.assertEquals('b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9', jrnl['journal_uuid'])
        self.assertEquals('http://jfs.example.org/index.php/jfs', jrnl['journal_url'])

    def test_statement(self):
        deposit = """
 <entry xmlns="http://www.w3.org/2005/Atom"
        xmlns:dcterms="http://purl.org/dc/terms/"
        xmlns:pkp="http://pkp.sfu.ca/SWORD">
    <email>journal_manager@example.com</email>
    <title>Journal of Foo Studies</title>
    <pkp:issn>1234-123x</pkp:issn>
    <pkp:journal_url>http://jfs.example.org/index.php/jfs</pkp:journal_url>
    <pkp:publisherName>Publ Name</pkp:publisherName>
    <pkp:publisherUrl>http://pub.example.com</pkp:publisherUrl>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2013-10-07T17:17:08Z</updated>
    <pkp:content size="102400" checksumType="sha1" volume="4" issue = "3" pubdate = "2011-04-25" checksumValue="bd4a9b642562547754086de2dab26b7d">http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip</pkp:content>
</entry>
        """
        r = requests.post(
            'http://localhost:9999/api/sword/2.0/col-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9',
            data=deposit,
            headers={
                'Content-type': 'text/xml; charset=UTF-8'
            }
        )
        r = requests.get(
            'http://localhost:9999/api/sword/2.0/cont-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9/1225c695-cfb8-4ebb-aaaa-80da344efa6a/state')
        self.assertEquals(200, r.status_code)
        self.assertEquals('UTF-8', r.encoding)
        root = ET.fromstring(r.content, parser=XMLParser(encoding='UTF-8'))
        feedcat = root.find('{http://www.w3.org/2005/Atom}category')
        self.assertEquals('State', feedcat.attrib['label'])
        entry_cat = root.findall('.//entry:entry/entry:category', namespaces)
        self.assertEquals(1, len(entry_cat))
        self.assertEquals('Original Deposit', entry_cat[0].attrib['label'])

    def test_edit_deposit(self):
        deposit = """
 <entry xmlns="http://www.w3.org/2005/Atom"
        xmlns:dcterms="http://purl.org/dc/terms/"
        xmlns:pkp="http://pkp.sfu.ca/SWORD">
    <email>journal_manager@example.com</email>
    <title>Journal of Foo Studies</title>
    <pkp:issn>1234-123x</pkp:issn>
    <pkp:journal_url>http://jfs.example.org/index.php/jfs</pkp:journal_url>
    <pkp:publisherName>Publ Name</pkp:publisherName>
    <pkp:publisherUrl>http://pub.example.com</pkp:publisherUrl>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2013-10-07T17:17:08Z</updated>
    <pkp:content size="102400" checksumType="sha1" volume="4" issue = "3" pubdate = "2011-04-25" checksumValue="bd4a9b642562547754086de2dab26b7d">http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip</pkp:content>
</entry>
        """
        r = requests.post(
            'http://localhost:9999/api/sword/2.0/col-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9',
            data=deposit,
            headers={
                'Content-type': 'text/xml; charset=UTF-8'
            }
        )
        edit = """
 <entry xmlns="http://www.w3.org/2005/Atom"
        xmlns:dcterms="http://purl.org/dc/terms/"
        xmlns:pkp="http://pkp.sfu.ca/SWORD">
    <email>journal_manager@example.com</email>
    <title>Journal of Bar Studies</title>
    <pkp:issn>1234-123x</pkp:issn>
    <pkp:journal_url>http://jfs.example.org/index.php/jfs</pkp:journal_url>
    <pkp:publisherName>Publ Name</pkp:publisherName>
    <pkp:publisherUrl>http://pub.example.com</pkp:publisherUrl>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2013-10-07T17:17:08Z</updated>
    <pkp:content size="102400" checksumType="sha1" volume="4" issue="3" pubdate="2011-04-25" checksumValue="bd4a9b642562547754086de2dab26b7d">http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip</pkp:content>
</entry>
        """
        r = requests.put(
            'http://localhost:9999/api/sword/2.0/cont-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            data=edit,
            headers={
                'Content-type': 'text/xml; charset=UTF-8'
            }
        )
        print r.content
        self.assertEquals(201, r.status_code)
        self.assertEquals(
            '/api/sword/2.0/cont-iri/b83b87bd-c70f-46e7-ae5e-6ecfeadad4d9/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            r.headers['location']
        )
        mysql = get_connection()
        cursor = mysql.cursor()
        cursor.execute('SELECT * FROM deposits')
        deposits = cursor.fetchall()
        self.assertEquals(2, len(deposits))
        self.assertEquals('1225c695-cfb8-4ebb-aaaa-80da344efa6a',
                          deposits[0]['deposit_uuid'])
        self.assertEquals('1225c695-cfb8-4ebb-aaaa-80da344efa6a',
                          deposits[1]['deposit_uuid'])
        self.assertEquals('edit', deposits[1]['action'])
        cursor.execute('SELECT * FROM journals')
        journals = list(cursor.fetchall())
        self.assertEquals(
            'http://jfs.example.org/index.php/jfs', journals[0]['journal_url'])


pkppln.config_file_name = 'config_test.cfg'
with_server = True
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

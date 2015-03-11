"""Tests for creating a deposit."""

import unittest
import sys
import xml.etree.ElementTree as ET
from os.path import abspath, dirname
from sword2 import Connection, Entry

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase


class CreateDepositTestCase(PkpPlnTestCase):

    @classmethod
    def setUpClass(self):
        super(CreateDepositTestCase, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(CreateDepositTestCase, self).tearDownClass()

    def test_deposit(self):
        c = Connection(
            service_document_iri='http://localhost:9999/api/sword/2.0/sd-iri',
            on_behalf_of='foo',
            keep_history=False,
            cache_deposit_receipts=False,
        )
        c.get_service_document()
        ws = c.sd.workspaces[0][1][0]
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/col-iri/foo',
            ws.href
        )

        e = Entry(
            id='urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            title='Journal of Foo Studies',
        )
        for ns in pkppln.namespaces.keys():
            e.register_namespace(ns, pkppln.namespaces[ns])

        e.add_fields(
            entry_email='example@example.com',
            pkp_issn='1234-123x',
            pkp_journal_url='http://jfs.example.org/index.php/jfs',
            pkp_publisherName='Publ Name',
            pkp_publisherUrl='http://pub.example.com'
        )
        content = ET.SubElement(
            e.entry,
            '{http://pkp.sfu.ca/SWORD}content',
            {
                'size': '102400',
                'checksumType': 'sha1',
                'volume': '4',
                'issue': '3',
                'pubdate': '2011-04-25',
                'checksumValue': 'bd4a9b642562547754086de2dab26b7d'
            }
        )
        content.text = 'http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip'
        reciept = c.create(col_iri=ws.href, metadata_entry=e)

        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/cont-iri/foo/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            reciept.edit
        )
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/cont-iri/foo/1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            reciept.cont_iri
        )
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/cont-iri/foo/1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            reciept.edit_media
        )
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/cont-iri/foo/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            reciept.location
        )
        deposit = pkppln.get_deposit(
            '1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            self.handle
        )[0]
        self.assertIsNotNone(deposit)
        self.assertEquals(
            '1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            deposit['deposit_uuid']
        )
        self.assertEquals(
                          'http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip', 
                          deposit['deposit_url']
                          )
        self.assertEquals(36, len(deposit['file_uuid']))

    def test_edit_deposit(self):
        c = Connection(
            service_document_iri='http://localhost:9999/api/sword/2.0/sd-iri',
            on_behalf_of='foo',
            keep_history=False,
            cache_deposit_receipts=False,
        )
        c.get_service_document()
        ws = c.sd.workspaces[0][1][0]
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/col-iri/foo',
            ws.href
        )

        e = Entry(
            id='urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            title='Journal of Foo Studies',
        )
        for ns in pkppln.namespaces.keys():
            e.register_namespace(ns, pkppln.namespaces[ns])

        e.add_fields(
            entry_email='example@example.com',
            pkp_issn='1234-123x',
            pkp_journal_url='http://jfs.example.org/index.php/jfs',
            pkp_publisherName='Publ Name',
            pkp_publisherUrl='http://pub.example.com'
        )
        content = ET.SubElement(
            e.entry,
            '{http://pkp.sfu.ca/SWORD}content',
            {
                'size': '102400',
                'checksumType': 'sha1',
                'volume': '4',
                'issue': '3',
                'pubdate': '2011-04-25',
                'checksumValue': 'bd4a9b642562547754086de2dab26b7d'
            }
        )
        content.text = 'http://jfs.example.org/download/1225c695-cfb8-4ebb-aaaa-80da344efa6a.zip'
        reciept = c.create(col_iri=ws.href, metadata_entry=e)
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/cont-iri/foo/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            reciept.location
        )
        content.text = 'http://jfs.example.org/download/1225c695.zip'
        reciept = c.update(metadata_entry=e, edit_iri=reciept.location)
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/cont-iri/foo/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit',
            reciept.location
        )        
        deposits = pkppln.get_deposit(
            '1225c695-cfb8-4ebb-aaaa-80da344efa6a',
            self.handle
        )
        self.assertEquals(len(deposits), 2)



pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

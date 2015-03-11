"""Tests for creating a deposit."""

import unittest
import sys
from os.path import abspath, dirname
from sword2 import Connection, sword2_logging
import logging

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase


class ServiceDocumentTestCase(PkpPlnTestCase):

    @classmethod
    def setUpClass(self):
        super(ServiceDocumentTestCase, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        super(ServiceDocumentTestCase, self).tearDownClass()

    def test_servicedocument(self):
        c = Connection(
            service_document_iri='http://localhost:9999/api/sword/2.0/sd-iri',
            on_behalf_of='foo',
            keep_history=False,
            cache_deposit_receipts=False,
        )
        c.get_service_document()
        self.assertTrue(c.sd.parsed)
        self.assertTrue(c.sd.valid)
        self.assertEquals(1, len(c.sd.workspaces))
        title = c.sd.workspaces[0][0]
        self.assertEquals('PKP PLN deposit for foo', title)
        self.assertEquals(1000, c.sd.maxUploadSize)
        ws = c.sd.workspaces[0][1][0]
        self.assertEquals(['application/atom+xml;type=entry'], ws.accept)
        self.assertTrue(ws.mediation)
        dom = c.sd.service_dom

    def test_collection_iri(self):
        c = Connection(
            service_document_iri='http://localhost:9999/api/sword/2.0/sd-iri',
            on_behalf_of='foo',
            keep_history=False,
            cache_deposit_receipts=False,
        )
        c.get_service_document()
        coll = c.sd.service_dom.find(
            './/app:collection[1]',
            pkppln.namespaces
        )
        self.assertIsNotNone(coll)
        self.assertEquals(
            'http://localhost:9999/api/sword/2.0/col-iri/foo',
            coll.attrib['href']
        )

    def test_terms(self):
        c = Connection(
            service_document_iri='http://localhost:9999/api/sword/2.0/sd-iri',
            on_behalf_of='foo',
            keep_history=False,
            cache_deposit_receipts=False,
        )
        c.get_service_document()
        dom = c.sd.service_dom
        entries = dom.findall('.//{http://pkp.sfu.ca/SWORD}terms_of_use/*')
        self.assertEquals(entries[0].text.strip(), u'I am good to go.')
        self.assertEquals(entries[1].text.strip(), u'U+00E9: \xe9')
        self.assertEquals(entries[2].text.strip(), u'U+20AC: \u20AC')
        self.assertEquals(
            entries[3].text.strip(), u'U+201C U+201D: \u201c \u201d')
        self.assertEquals(
            entries[4].text.strip(), u'U+2039 U+203A: \u2039 \u203a')


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

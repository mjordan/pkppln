
import unittest
import sys
import xml.etree.ElementTree as ET
from os.path import abspath, dirname
import os.path
from argparse import Namespace

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase
from services.microservices.harvest import Harvest

import requests
from urllib import url2pathname

class LocalFileAdapter(requests.adapters.BaseAdapter):
    """Protocol Adapter to allow Requests to GET file:// URLs

    @todo: Properly handle non-empty hostname portions.
    """

    @staticmethod
    def _chkpath(method, path):
        """Return an HTTP status for the given filesystem path."""
        if method.lower() in ('put', 'delete'):
            return 501, "Not Implemented"  # TODO
        elif method.lower() not in ('get', 'head'):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req, **kwargs):
        path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                response.raw = open(path, 'rb')
            except (OSError, IOError), err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass

class HarvestDepositTestCase(PkpPlnTestCase):

    @classmethod
    def setUpClass(self):
        super(HarvestDepositTestCase, self).setUpClass()
        self.requests_session = requests.session()
        self.requests_session.mount('file://', LocalFileAdapter())

    @classmethod
    def tearDownClass(self):
        #super(HarvestDepositTestCase, self).tearDownClass()
        pass

    def test_harvest(self):
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
            db=self.handle
        )[0]
        deposit['deposit_url'] = 'file:///Users/mjoyce/Sites/pkppln2/tests/data/402a6e97-dbd2-4aba-a3e4-234aabb4314c'
        cmd = Harvest()
        cmd.args = Namespace(verbose=2, force=False, dry_run=False)
        cmd.set_request_session(self.requests_session)
        cmd.process_deposit(deposit)

        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
        )[0]
        print deposit
        
        self.assertEquals('harvested', deposit['processing_state'])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

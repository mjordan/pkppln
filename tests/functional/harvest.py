import unittest
import sys
from os.path import abspath, dirname
import os.path
from argparse import Namespace
import requests
from urllib import url2pathname

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))
import pkppln
from tests.processing_testcase import ProcessingTestCase
from services.microservices.harvest import Harvest


base_path = dirname(dirname(dirname(abspath(__file__))))


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


class HarvestTestCase(ProcessingTestCase):

    @classmethod
    def setUpClass(self):
        print 'setupclass'
        super(HarvestTestCase, self).setUpClass()
        self.requests_session = requests.session()
        self.requests_session.mount('file://', LocalFileAdapter())

    @classmethod
    def tearDownClass(self):
        print 'teardown'
        super(HarvestTestCase, self).tearDownClass()

    def runTest(self):
        print 'runtest'
        self.test_harvest()

    def test_harvest(self):
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
            db=self.handle
        )[0]
        deposit['deposit_url'] = 'file://' + base_path + \
            '/tests/data/C7DD3B7D-8AD5-445A-89C1-EFB7CCBD4466'
        args = Namespace(verbose=1, force=False, 
                         dry_run=False, config='config_test.cfg')
        cmd = Harvest(args)
        cmd.set_request_session(self.requests_session)
        cmd.process_deposit(deposit)

        # don't use db=self.handle here. It returns the cached
        # deposit. Let pkppln get a new db connection instead.
        deposit = pkppln.get_deposit(
            '61AEF065-71DE-93AA-02B0-5618ABAC2393',
        )[0]

        self.assertEquals('harvested', deposit['processing_state'])


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()

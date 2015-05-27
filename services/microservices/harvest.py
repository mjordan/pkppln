from services.PlnService import PlnService
import pkppln
import requests
import os
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


class Harvest(PlnService):

    """Harvest a deposit from an OJS instance."""

    def __init__(self, args):
        super(Harvest, self).__init__(args)
        self.request_session = requests.session()
        self.request_session.mount('file://', LocalFileAdapter())

    def state_before(self):
        return 'depositedByJournal'

    def state_after(self):
        return 'harvested'

    def set_request_session(self, request_session):
        self.request_session = request_session

    def execute(self, deposit):
        uuid = deposit['file_uuid']
        url = deposit['deposit_url']
        self.output(1, 'Fetching ' + url)
        filename = uuid

        harvest_dir = pkppln.microservice_directory(self.state_after())
        harvest_bag = os.path.join(harvest_dir, filename)

        r = self.request_session.get(url, stream=True)
        self.output(2, 'HTTP ' + str(r.status_code))
        if r.status_code == 404:
            raise Exception("Deposit URL %s not found" % (url))
        if r.status_code != 200:
            raise Exception("HTTP Error: " + str(r.status_code))
        f = open(harvest_bag, 'wb')
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
        self.output(2, 'Saved to ' + harvest_bag)

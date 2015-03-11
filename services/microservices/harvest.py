from services.PlnService import PlnService
import pkppln
import requests
import os


class Harvest(PlnService):

    """Harvest a deposit from an OJS instance."""

    def __init__(self):
        super(Harvest, self).__init__()
        self.request_session = requests.session()

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

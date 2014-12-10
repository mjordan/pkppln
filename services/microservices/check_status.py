import pkppln
from services.PlnService import PlnService
from sword.client import SwordClient
from xml.etree import ElementTree as ET
from urlparse import urlparse


class CheckStatus(PlnService):

    """Check the status of a deposit in a LOCKSSOMatic instance."""

    def state_before(self):
        return 'deposited'

    def state_after(self):
        return 'lockssAgreement'

    def execute(self, deposit):
        journal_uuid = deposit['journal_uuid']
        config = pkppln.get_config()
        client = SwordClient(
            config.get('URLs', 'lockssomatic_base_url'),
            journal_uuid
        )
        service_document = client.statement(deposit)
        root = ET.fromstring(service_document)
        statuses = root.findall('.//lom:server', pkppln.namespaces)
        print deposit['deposit_url']
        for status in statuses:
            url = urlparse(status.attrib['src'])
            print ':'.join([url.hostname, status.attrib['state']])

        return '', ''

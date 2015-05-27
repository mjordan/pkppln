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
        journal = pkppln.get_journal_by_id(deposit['journal_id'])
        journal_uuid = journal['journal_uuid']
        config = pkppln.get_config()
        client = SwordClient(
            config.get('URLs', 'lom_base_url'),
            journal['journal_url'],
            journal_uuid
        )
        statement = client.statement(deposit)
        root = ET.fromstring(statement)
        statuses = root.findall('.//lom:server', pkppln.namespaces)
        print deposit['deposit_url']
        for status in statuses:
            url = urlparse(status.attrib['src'])
            print ':'.join([url.hostname, status.attrib['state']])
            # DO STUFF HERE.

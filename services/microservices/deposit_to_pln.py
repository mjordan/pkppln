import os
import pkppln
from services.PlnService import PlnService
from sword.client import SwordClient


class DepositToPln(PlnService):

    """Deposit a reserialized bag into LOCKSSOMatic for eventual deposit
    into the PLN."""

    def state_before(self):
        return 'staged'

    def state_after(self):
        return 'deposited'

    def execute(self, deposit):
        journal = pkppln.get_journal_by_id(
            deposit['journal_id'],
            db=self.handle
        )

        journal_uuid = journal['journal_uuid']
        file_uuid = deposit['file_uuid']
        config = pkppln.get_config()
        journal = pkppln.get_journal_by_id(deposit['journal_id'])

        client = SwordClient(
            config.get('URLs', 'lom_base_url'),
            journal['journal_url'],
            journal_uuid
        )

        filename = '.'.join([journal_uuid, file_uuid, 'tar.gz'])
        filepath = os.path.join(
            config.get('Paths', 'staging_root'),
            journal_uuid,
            filename
        )

        url = '/'.join([
            config.get('URLs', 'lom_base_url'),
            'mypln',
            journal_uuid,
            filename
        ])

        receipt, content = client.create_deposit(
            url, filepath, deposit, journal
        )

        pkppln.record_deposit(deposit, receipt, db=self.handle)

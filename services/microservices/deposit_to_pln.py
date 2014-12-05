import os
import pkppln
from services.PlnService import PlnService
from sword.client import SwordClient


class DepositToPln(PlnService):

    def state_before(self):
        return 'staged'

    def state_after(self):
        return 'deposited'

    def execute(self, deposit):
        journal_uuid = deposit['journal_uuid']
        deposit_uuid = deposit['deposit_uuid']
        config = pkppln.get_config()
        journal = pkppln.get_journal(deposit['deposit_uuid'])

        client = SwordClient(
            config.get('URLs', 'lockssomatic_base_url'),
            journal_uuid
        )

        filename = '.'.join([journal_uuid, deposit_uuid, 'tar.gz'])
        filepath = os.path.join(
            config.get('Paths', 'staging_root'),
            deposit['journal_uuid'],
            filename
        )

        url = '/'.join([
            config.get('URLs', 'sword_server_base_url'),
            'mypln',
            journal_uuid,
            filename
        ])

        print client.create_deposit(url, filepath, deposit, journal)

        # staged url

        return 'failed', 'failed'

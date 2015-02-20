import os
from services.PlnService import PlnService
import pkppln
import shutil


class StageBag(PlnService):

    """Move the serialized bag file into the staging area, so that
    LOCKSSOMatic may harvest it later."""

    def state_before(self):
        return 'reserialized'

    def state_after(self):
        return 'staged'

    def execute(self, deposit):
        journal_uuid = deposit['journal_uuid']
        deposit_uuid = deposit['deposit_uuid']
        config = pkppln.get_config()

        filename = '.'.join([journal_uuid, deposit_uuid, 'tar.gz'])

        source_file = pkppln.input_path('reserialized', '', filename)

        self.output(2, 'Staging from ' + source_file)

        dest_path = os.path.join(
            config.get('Paths', 'staging_root'),
            journal_uuid
        )
        dest_file = os.path.join(dest_path, filename)

        self.output(2, 'Staging to ' + dest_file)

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        shutil.move(source_file, dest_file)

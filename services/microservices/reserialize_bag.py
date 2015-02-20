from services.PlnService import PlnService
import os
import bagit
import pkppln
import tarfile


class ReserializeBag(PlnService):

    """Reserialize/repackage a bag into a .tar.gz file."""

    def state_before(self):
        return 'contentValidated'

    def state_after(self):
        return 'reserialized'

    def execute(self, deposit):
        config = pkppln.get_config()

        uuid = deposit['deposit_uuid']
        expanded_path = pkppln.microservice_directory('bagValidated', uuid)
        bag_path = os.path.join(expanded_path, 'bag')
        bag = bagit.Bag(bag_path)
        bag.info['External-identifier'] = uuid
        bag.info['PKP-PLN-Journal-UUID'] = deposit['journal_uuid']
        bag.info['PKP-PLN-Deposit-UUID'] = uuid
        bag.save(manifests=True)

        bag.validate()

        tar_filename = '.'.join([deposit['journal_uuid'], uuid, 'tar.gz'])
        tar_path = os.path.join(
            config.get('Paths', 'processing_root'),
            self.state_after(),
        )

        if not os.path.exists(tar_path):
            os.makedirs(tar_path)

        tar_filepath = os.path.join(tar_path, tar_filename)

        self.output(1, 'Saving tar.gz to ' + tar_filepath)

        tar_file = tarfile.open(tar_filepath, 'w:gz')
        tar_file.add(bag_path)

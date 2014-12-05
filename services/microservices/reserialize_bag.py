from services.PlnService import PlnService
import os
import bagit
import pkppln
import tarfile


class ReserializeBag(PlnService):

    def state_before(self):
        return 'contentValidated'

    def state_after(self):
        return 'reserialized'

    def execute(self, deposit):
        result = 'success'
        message = ''
        config = pkppln.get_config()

        uuid = deposit['deposit_uuid']
        expanded_path = pkppln.microservice_directory('bagValidated', uuid)
        bag_path = os.path.join(expanded_path, 'bag')
        bag = bagit.Bag(bag_path)
        bag.info['External-identifier'] = uuid
        bag.info['PKP-PLN-Journal-UUID'] = deposit['journal_uuid']
        bag.info['PKP-PLN-Deposit-UUID'] = uuid
        bag.save(manifests=True)

        try:
            bag.validate()
        except Exception as error:
            result = 'failed'
            message += error.message

        tar_filename = '.'.join([deposit['journal_uuid'], uuid, 'tar.gz'])
        tar_filepath = os.path.join(
            config.get('Paths', 'processing_root'),
            self.state_after(),
            tar_filename
        )

        self.output(1, 'Saving tar.gz to ' + tar_filepath)

        try:
            tar_file = tarfile.open(tar_filepath, 'w:gz')
            tar_file.add(bag_path)
        except Exception as error:
            result = 'failed'
            message += error.message

        return result, message

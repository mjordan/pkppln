import os
from services.PlnService import PlnService
import pkppln
import bagit
import zipfile
import shutil


class ValidateBag(PlnService):

    """Validate a bag in a deposit"""

    def state_before(self):
        return 'payloadVerified'

    def state_after(self):
        return 'bagValidated'

    def execute(self, deposit):
        url = deposit['deposit_url']
        uuid = deposit['deposit_uuid']
        filename = pkppln.deposit_filename(url)
        filepath = pkppln.input_path('harvested', [uuid], filename)
        self.output(1, 'Opening ' + filepath)

        zfile = zipfile.ZipFile(filepath)
        for name in zfile.namelist():
            self.output(2, ' * ' + name)
            if name.startswith('/') or '..' in name:
                raise Exception(
                    'Suspicious file name %s in zipped bag' % (name)
                )

        expanded_path = pkppln.microservice_directory(self.state_after(), uuid)
        if os.path.exists(expanded_path):
            self.output(1, 'Removing old bag ' + expanded_path)
            shutil.rmtree(expanded_path)

        zfile.extractall(expanded_path)
        bag_path = os.path.join(expanded_path, 'bag')
        self.output(1, 'extracted to ' + bag_path)

        bag = bagit.Bag(bag_path)
        if not bag.is_valid():
            raise Exception('Bag is not valid.')
        self.output(2, 'bag is valid.')

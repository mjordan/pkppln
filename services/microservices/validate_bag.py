import os
from services.PlnService import PlnService
import pkppln
import bagit
import zipfile


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
                return 'failure', 'Suspicious filename %s in zipped bag' % (name)

        expanded_path = pkppln.microservice_directory(self.state_after(), uuid)
        zfile.extractall(expanded_path)
        bagpath = os.path.join(expanded_path, 'bag')
        self.output(1, 'extracted to ' + bagpath)

        try:
            bag = bagit.Bag(bagpath)
            if not bag.is_valid():
                return 'failure', 'Bag is not valid.'
            else:
                self.output(2, 'bag is valid.')
        except Exception as exception:
            return 'failure', exception.message

        return 'success', ''

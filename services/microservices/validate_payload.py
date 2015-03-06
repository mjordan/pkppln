from services.PlnService import PlnService
import pkppln
import os
import math


class ValidatePayload(PlnService):

    """Validate a harvested deposit by checking file size and checksum"""

    def state_before(self):
        return 'harvested'

    def state_after(self):
        return 'payloadVerified'

    def execute(self, deposit):
        sha1 = deposit['deposit_sha1']
        size = deposit['deposit_size']
        filename = deposit['file_uuid']
        filepath = pkppln.input_path('harvested', filename=filename)
        self.output(1, 'validating ' + filename)
        bs = os.path.getsize(filepath)
        kb = int(math.ceil(float(bs) / 1000.0))
        if size != kb:
            raise Exception('File sizes do not match: \n\t%s expected\n\t%s actual' % (size, kb))
        self.output(1, 'File sizes match')

        # Verify SHA-1 checksum reported in the SWORD deposit.
        calculated_sha1 = pkppln.file_sha1(filepath)
        if sha1 != calculated_sha1:
            raise 'SHA-1 does not match: \n\t%s expected\n\t%s calculated' % (sha1, calculated_sha1)
        self.output(1, 'Checksums match')

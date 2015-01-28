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
        uuid = deposit['deposit_uuid']
        sha1 = deposit['sha1_value']
        size = deposit['size']
        filename = pkppln.deposit_filename(deposit['deposit_url'])
        filepath = pkppln.input_path('harvested', [uuid], filename)
        self.output(1, 'validating ' + filename)
        self.output(2, 'looking for\n' + filepath)
        bs = os.path.getsize(filepath)
        kb = int(math.ceil(float(bs) / 1000.0))
        if size != kb:
            return 'failure', 'File sizes do not match: \n\t%s expected\n\t%s actual' % (size, kb)
        self.output(1, 'File sizes match')

        # Verify SHA-1 checksum reported in the SWORD deposit.
        calculated_sha1 = pkppln.file_sha1(filepath)
        if sha1 != calculated_sha1:
            return 'failure', 'SHA-1 does not match: \n\t%s expected\n\t%s calculated' % (sha1, calculated_sha1)
        self.output(1, 'Checksums match')
        return 'success', ''

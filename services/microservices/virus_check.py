import os
from datetime import datetime
from services.PlnService import PlnService
import pkppln
import bagit
import base64
from xml.etree import ElementTree
import clamd
from tempfile import NamedTemporaryFile


class VirusCheck(PlnService):

    """Run a virus check on the contents of a deposit bag. Extracts all the
    mime-encoded content to a temporary directory and scans each one with
    clamd."""

    def __init__(self, args):
        PlnService.__init__(self, args)
        clam_socket = pkppln.get_config().get('Paths', 'clamd_socket')
        self.clam = clamd.ClamdUnixSocket(path=clam_socket)
        self.filecount = 0
        self.report = {}

    def state_before(self):
        return 'bagValidated'

    def state_after(self):
        return 'virusChecked'

    def scan(self, embed):
        filename = embed.get('filename')
        self.output(2, 'checking ' + filename)
        if len(filename):
            self.filecount += 1
            tmpfile = NamedTemporaryFile(delete=False)
            tmpfile.write(base64.decodestring(embed.text))
            tmpfile.close()
            result = self.clam.scan(tmpfile.name)
            self.report[filename] = result[tmpfile.name]
            os.unlink(tmpfile.name)

    def execute(self, deposit):
        srv_status = 'success'
        error = ''

        file_uuid = deposit['file_uuid']
        expanded_path = pkppln.microservice_directory('bagValidated', file_uuid)
        bag_path = os.path.join(expanded_path, 'bag')
        report_path = os.path.join(bag_path, 'data', 'virus_scan.txt')
        report_file = open(report_path, 'w')
        report_file.write('# Virus scan started ' + str(datetime.now())
                          + ' by ' + self.clam.version() + '\n')
        bag_path = os.path.join(expanded_path, 'bag')

        bag = bagit.Bag(bag_path)
        for payload_file in bag.payload_files():
            if payload_file.startswith('data/terms'):
                continue
            if not payload_file.endswith('.xml'):
                continue
            payload_xml = os.path.join(bag_path, payload_file)
            if not os.path.isfile(payload_xml):
                return 'failed', 'Cannot find export XML in ' + payload_xml

            self.output(2, 'Parsing ' + payload_xml)
            document = ElementTree.parse(payload_xml)
            embeded = document.findall('.//embed')
            self.output(
                1, payload_file + ' has ' + str(len(embeded)) + ' docs.')
            for embed in embeded:
                self.scan(embed)

        for filename in self.report:
            status = self.report[filename]
            report_file.write(filename + '\t' + status[0] + '\n')
            if(status[0] != 'OK'):
                srv_status = 'failure'
                error += 'Virus found: ' + status[1] + '\n'
                report_file.write('WARNING: Virus found: ' + status[1] + '\n')
        report_file.write('# Virus scan complete at ' + str(datetime.now()))
        report_file.close()

        return srv_status, error

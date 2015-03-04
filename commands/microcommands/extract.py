from commands.PlnCommand import PlnCommand
import bagit
import pkppln
import zipfile
import os
import shutil
from xml.etree import ElementTree
import base64
from os.path import dirname


class Extract(PlnCommand):

    def description(self):
        return "Extract the content of one deposit."

    def add_args(self, parser):
        parser.add_argument('deposit',
                            help='Deposit to process')

    def execute(self, args):
        if args.deposit is None:
            return 'No deposit'
        uuid = args.deposit
        filepath = pkppln.input_path('harvested', [uuid], uuid)
        self.output(1, 'Opening ' + filepath)

        zfile = zipfile.ZipFile(filepath)
        for name in zfile.namelist():
            self.output(2, ' * ' + name)
            if name.startswith('/') or '..' in name:
                raise Exception(
                    'Suspicious file name %s in zipped bag' % (name)
                )

        expanded_path = pkppln.microservice_directory('extracted', uuid)
        if os.path.exists(expanded_path):
            self.output(1, 'Removing old bag ' + expanded_path)
            shutil.rmtree(expanded_path)

        zfile.extractall(expanded_path)
        bag_path = os.path.join(expanded_path, 'bag')
        self.output(1, 'extracted to ' + bag_path)

        bag = bagit.Bag(bag_path)
        if not bag.is_valid():
            raise Exception('Bag is not valid.')
        self.output(1, 'bag is valid.')

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
                filename = embed.get('filename')
                if len(filename):
                    fp = os.path.join(dirname(payload_xml), filename)
                    self.output(1, ' * ' + fp)
                    f = open(fp, 'w')
                    f.write(base64.decodestring(embed.text))

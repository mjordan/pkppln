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
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--deposit',
            help='Deposit to process',
            action='append',
        )
        group.add_argument(
            '--all',
            help='Extract all deposits',
            action='store_true'
        )

    def unzip(self, filepath):
        self.output(1, 'Opening ' + filepath)

        zfile = zipfile.ZipFile(filepath)
        for name in zfile.namelist():
            self.output(2, ' * ' + name)
            if name.startswith('/') or '..' in name:
                raise Exception(
                    'Suspicious file name %s in zipped bag' % (name)
                )

        uuid = pkppln.deposit_filename(filepath)
        expanded_path = pkppln.microservice_directory('extracted', uuid)
        if os.path.exists(expanded_path):
            self.output(1, 'Removing old bag ' + expanded_path)
            shutil.rmtree(expanded_path)

        zfile.extractall(expanded_path)
        bag_path = os.path.join(expanded_path, 'bag')
        self.output(1, 'extracted to ' + bag_path)
        return bag_path

    def validate_bag(self, bag_path):
        bag = bagit.Bag(bag_path)
        if not bag.is_valid():
            raise Exception('Bag is not valid.')
        self.output(1, 'bag is valid.')
        return bag

    def write_embed(self, embed, path):
        filename = embed.get('filename')
        if filename.startswith('/') or '..' in filename:
            raise Exception(
                'Suspicious file name %s in exported XML' % (filename)
            )
        fp = os.path.join(path, filename)
        self.output(1, ' * ' + filename)
        if embed.text is None:
            self.output(0, filename + ' has no content')
            return

        try:
            f = open(fp, 'w')
            f.write(base64.decodestring(embed.text))
        except Exception as e:
            self.output(0, 'Cannot write ' + filename + ': ' + str(e))

    def extract(self, bag):
        for payload_file in bag.payload_files():
            if payload_file.startswith('data/terms'):
                continue
            if not payload_file.endswith('.xml'):
                continue
            payload_xml = os.path.join(bag.path, payload_file)
            if not os.path.isfile(payload_xml):
                return 'failed', 'Cannot find export XML in ' + payload_xml

            self.output(2, 'Parsing ' + payload_xml)
            document = ElementTree.parse(payload_xml)
            embeded = document.findall('.//embed')
            self.output(
                1, payload_file + ' has ' + str(len(embeded)) + ' docs.')
            for embed in embeded:
                self.write_embed(embed, dirname(payload_xml))

    def execute(self, args):
        deposits = args.deposit
        if args.all:
            deposits = [d['file_uuid'] for d in pkppln.db_query(
                'SELECT file_uuid FROM deposits',
                db=self.handle
            )]

        for file_uuid in deposits:
            filepath = pkppln.input_path('harvested', [], file_uuid)
            bag_path = self.unzip(filepath)
            bag = self.validate_bag(bag_path)
            self.extract(bag)

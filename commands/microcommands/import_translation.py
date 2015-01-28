import pkppln
from commands.PlnCommand import PlnCommand
from lxml import etree as et
from lxml.etree import Element, SubElement, Comment
from datetime import datetime


class ImportTranslation(PlnCommand):

    def description(self):
        return "Import terms of service from a translation XML file."

    # @TODO add optional update param.
    def add_args(self, parser):
        parser.add_argument(
            'file',
            help='Path to XML file to import'
        )

    def execute(self, args):
        tree = et.parse(args.file)
        root = tree.getroot()
        locale = root.get('name')
        s = ''
        for message in root.xpath('//message'):
            key = message.get('key')
            term = pkppln.get_localized_term(key, locale)
            if term is None:
                term = {
                    'key': key,
                    'current': 'Yes',
                    'language': locale,
                }
            term['text'] = message.text
            term['updated'] = datetime.now()
            # insert or update the term.
            s += str(term) + '\n'
        return s

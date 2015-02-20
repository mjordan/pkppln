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
        terms = pkppln.get_all_terms(db=self.handle)
        for term in terms:
            xt = root.xpath('//message[@key="' + term['key_code'] + '"]')
            if len(xt) == 0:
                # @TODO should this be an exception and rollback?
                self.output(-1, "Missing term: " + term['key_code'])
                continue

            translated = {}
            translated['weight'] = term['weight']
            translated['lang_code'] = locale
            translated['key_code'] = term['key_code']
            translated['content'] = xt[0].text

            try:
                pkppln.edit_term(translated, self.handle)
            except:
                self.handle.rollback()
                raise

            self.output(1, term['key_code'])
        self.handle.commit()


import pkppln
from commands.PlnCommand import PlnCommand
from lxml import etree as et
from lxml.etree import Element, SubElement, Comment


class ExportTranslation(PlnCommand):

    def description(self):
        return "Export the terms of service to a translatable XML file."

    def execute(self, args):
        terms = pkppln.get_all_terms()
        locale = Element('locale', attrib={
            'name': "en_US",
            'full_name': "U.S. English",
        })

        locale.append(Comment(
            """
    * Localization strings.
    *
    * To use, change the locale name from en_US to the appropriate code
    * for your language, and change the full name to the proper name
    * of your language.
    *
    * Do not edit or change the message key attributes. Only edit the
    * text content of the message tags.
    """))

        for term in terms:
            message = SubElement(locale, 'message')
            message.set('key', term['key_code'])
            message.text = term['content']
        self.output(0, et.tostring(
            locale,
            pretty_print=True,
            encoding="UTF-8",
            xml_declaration=True
        ))

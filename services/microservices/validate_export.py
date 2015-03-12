from services.PlnService import PlnService
import pkppln
import os
import re
import bagit
from lxml import etree


class ValidateExport(PlnService):

    """Validate the XML exported from OJS. Also inserts some journal metaadata
    into the bag."""

    def __init__(self, args):
        PlnService.__init__(self, args)

    def state_before(self):
        return 'virusChecked'

    def state_after(self):
        return 'contentValidated'

    def execute(self, deposit):
        file_uuid = deposit['file_uuid']
        expanded_path = pkppln.microservice_directory('bagValidated', file_uuid)
        bag_path = os.path.join(expanded_path, 'bag')
        bag = bagit.Bag(bag_path)
        # this should probably be bag.entries.items()
        for payload_file in bag.payload_files():
            if payload_file.startswith('data/terms'):
                continue
            payload_xml = os.path.join(bag_path, payload_file)
            if not os.path.isfile(payload_xml):
                raise Exception('Cannot find export XML in ' + payload_xml)

            self.output(1, 'validating ' + payload_xml)
            parser = etree.XMLParser()
            document = etree.parse(payload_xml, parser=parser)

            systemId = document.docinfo.system_url
            if not re.match(r'http://pkp.sfu.ca/.*/dtds', systemId):
                raise('Suspicious DOCTYPE: ' + systemId)

            self.output(2, 'system id: ' + systemId)

            dtd = etree.DTD(systemId)
            result = dtd.validate(document)

            if result is False:
                message = ''
                for log in dtd.error_log:
                    message += "----\n"
                    message += ':'.join((payload_file, str(log.line),
                                         str(log.column), log.type_name,
                                         log.message))
                    message += '\n'
                raise Exception(message)
            else:
                self.output(2, 'validation passed')

            journal_xml = pkppln.get_journal_xml(file_uuid)
            journal_path = os.path.join(bag_path, 'data', 'journal_info.xml')
            journal_file = open(journal_path, 'w')
            journal_file.write(journal_xml)
            journal_file.close()
            self.output(2, 'saved journal info to ' + journal_path)

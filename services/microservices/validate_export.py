from services.PlnService import PlnService
import pkppln
import os
import re
import bagit
import requests
from lxml import etree


class ValidateExport(PlnService):

    def state_before(self):
        return 'virusChecked'

    def state_after(self):
        return 'contentValidated'

    def execute(self, deposit):
        result = 'success'
        message = ''

        uuid = deposit['deposit_uuid']
        expanded_path = pkppln.microservice_directory('bagValidated', uuid)
        bag_path = os.path.join(expanded_path, 'bag')
        bag = bagit.Bag(bag_path)
        # this should probably be bag.entries.items()
        for payload_file in bag.payload_files():
            if payload_file.startswith('data/terms'):
                continue
            payload_xml = os.path.join(bag_path, payload_file)
            if not os.path.isfile(payload_xml):
                return 'failed', 'Cannot find export XML in ' + payload_xml
            self.output(1, 'validating ' + payload_xml)
            parser = etree.XMLParser()
            try:
                document = etree.parse(payload_xml, parser=parser)
            except Exception as error:
                return 'failed', error.message
            systemId = document.docinfo.system_url
            if not re.match(r'http://pkp.sfu.ca/.*/dtds', systemId):
                return 'failed', 'Suspicious DOCTYPE: ' + systemId
            self.output(2, 'system id: ' + systemId)
#             result = None
#             try:
#                 dtd = etree.DTD(systemId)
#                 result = dtd.validate(document)
#             except Exception as error:
#                 return 'failed', error.message
# 
#             if result is False:
#                 for log in dtd.error_log:
#                     message += "----\n"
#                     message += ':'.join((payload_file, str(log.line),
#                                          str(log.column), log.type_name,
#                                          log.message))
#                     message += '\n'
#                 result = 'failure'
#             else:
#                 self.output(2, 'validation passed')

            journal_xml = pkppln.get_journal_info(uuid)
            journal_path = os.path.join(bag_path, 'data', 'journal_info.xml')
            journal_file = open(journal_path, 'w')
            journal_file.write(journal_xml)
            journal_file.close()
            self.output(2, 'saved journal info to ' + journal_path)

            return result, message

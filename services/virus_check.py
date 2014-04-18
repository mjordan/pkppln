"""
Script to check files harvested from OJS journals participating in the 
PKP PLN for viruses. Decodes base64 encoded files in <embed> elements,
writes them to a temp directory, checks them for viruses, then deletes
the temp directory.
"""

import os
import sys
import ConfigParser
import base64
from xml.etree import ElementTree
from datetime import datetime
import clamd 

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'check_deposit_for_viruses'
microservice_state = 'virusChecked'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on.
previous_microservice_state = 'unserialized'

def check(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit['deposit_uuid']
    outcome = 'success'
    error = ''

    path_to_unserialized_deposit = staging_server_common.get_input_path(previous_microservice_state, deposit_uuid)
    # We decode all of the base64-encoded files in the OJS XML
    # into a temporary directory so we can check them for viruses.
    path_to_temp_directory = os.path.join(path_to_unserialized_deposit, temp)
    if not os.path.exists(path_to_temp_directory):
        os.makedirs(path_to_temp_directory)

    # Extract all the files from the XML.
    # @todo: Determine if we are using articles.xml or issue.xml.
    path_to_xml = os.path.join(path_to_unserialized_deposit, 'articles_formatted.xml')
    try:
        document = ElementTree.parse(path_to_xml)
        for embed in document.findall('.//embed'):
            filename = embed.get('filename')
            # print embed.text
            # @todo: check for duplicate filenames
            file_to_scan = open(filename, "w")
            file_to_scan.write(base64.decodestring(embed.text))
            file_to_scan.close()
    except Exception as e:
        error = e
        outcome = 'failure'

    # If we hit an exception here, record it and exit.
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)
    sys.exit(1)

    # Write results of the virus check to virus_check.txt in same directory
    # as the existing deposit content files.
    path_to_virus_check_report = path = os.path.join(path_to_unserialized_deposit, 'virus_check.txt')

    try:
        cd = clamd.ClamdUnixSocket()
        clamav_version = clamd.version()
        report_file = open(path_to_virus_check_report, 'w')
        for root, _, files in os.walk(path_to_temp_directory):
            for content_file in files:
                fname = os.path.join(os.getcwd(), root, content_file)
                result = cd.scan(fname)
                # @todo: Include the virus name if possible.
                if result is None:
                    report_file.write("No virus found: " + fname + "\n")
                else:
                    report_file.write("WARNING: Virus found: " + fname + "\n")
        report_file.close()
    except Exception as e:
        error = e
        outcome = 'failure'

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

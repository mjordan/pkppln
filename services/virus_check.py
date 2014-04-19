"""
Script to check files harvested from OJS journals participating in the 
PKP PLN for viruses. Decodes base64 encoded files in <embed> elements,
writes them to a temp directory, checks them for viruses, then deletes
the temp directory.
"""

import os
import os.path
import sys
import shutil
import ConfigParser
import base64
import clamd
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'check_deposit_for_viruses'
microservice_state = 'virusChecked'
# The name of the directory under the processing root directory. One of
# 'havested', 'bagValidated', or 'reserialized'.    
input_directory = 'bagValidated'

def check(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit['deposit_uuid']
    outcome = 'success'
    error = ''

    path_to_unserialized_deposit = staging_server_common.get_input_path(input_directory, [deposit_uuid, deposit_uuid], 'data')
    # We decode all of the base64-encoded files in the OJS XML
    # into a temporary directory so we can check them for viruses.
    path_to_temp_directory = os.path.join(path_to_unserialized_deposit, 'tmp')
    if not os.path.exists(path_to_temp_directory):
        os.makedirs(path_to_temp_directory)

    # Extract all the files from the XML.
    try:
        # Determine if we are using articles.xml or issues.xml.
        if os.path.isfile(os.path.join(path_to_unserialized_deposit, 'articles.xml')):
            path_to_xml = os.path.join(path_to_unserialized_deposit, 'articles.xml')
        elif os.path.isfile(os.path.join(path_to_unserialized_deposit, 'issues.xml')):
            path_to_xml = os.path.join(path_to_unserialized_deposit, 'issues.xml')
        else:
            raise Exception("Can't find export XML file in %s" % (path_to_unserialized_deposit))
        document = ElementTree.parse(path_to_xml)
        # Increment a counter to use as a directory name for each file
        # to ensure we don't overwrite files with duplicate names.
        file_counter = 0
        for embed in document.findall('.//embed'):
            filename = embed.get('filename')
            if len(filename):
                # Increment the counter to get the directory name for the current file.
                file_counter = file_counter + 1
                path_to_file_to_scan = os.path.join(path_to_temp_directory, str(file_counter))
                if not os.path.exists(path_to_file_to_scan):
                    os.makedirs(path_to_file_to_scan)
                file_to_scan = open(os.path.join(path_to_file_to_scan, filename), "w")
                file_to_scan.write(base64.decodestring(embed.text))
                file_to_scan.close()
    except Exception as e:
        error = e
        outcome = 'failure'
        # If we hit an exception here, record it and exit.
        finished_on = datetime.now()
        staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
        staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)
        sys.exit(1)

    # Write results of the virus check to virus_check.txt in same directory
    # as the existing deposit content files.
    path_to_virus_check_report = path = os.path.join(path_to_unserialized_deposit, 'virus_check.txt')
    try:
        report_file = open(path_to_virus_check_report, 'w')
        cd = clamd.ClamdUnixSocket()
        clamav_version = cd.version()
        report_file.write("# Virus scan performed " + str(datetime.now()) + " by " + clamav_version + "\n")
        for root, _, files in os.walk(path_to_temp_directory):
            for content_file in files:
                fname = os.path.join(os.getcwd(), root, content_file)
                result = cd.scan(fname)
                # @todo: Include the virus name if possible.
                if result[fname][0] == 'OK':
                    report_file.write("No virus found: " + fname.split(os.sep)[-1] + "\n")
                else:
                    report_file.write("WARNING: Virus found: " + fname.split(os.sep)[-1] + ':' + result[fname][1] + "\n")
        report_file.close()
        # Remove temporary directory and its contents.
        shutil.rmtree(path_to_temp_directory)
    except Exception as e:
        error = e
        outcome = 'failure'

    finished_on = datetime.now()

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

"""
Script to verify OJS export XML, etc. from OJS journals participating in the 
PKP PLN for viruses.
"""

import os
import subprocess
import re
import ConfigParser
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'verify_deposit_structure'
microservice_state = 'contentVerified'
# The name of the directory under the processing root directory. One of
# 'havested', 'bagValidated', or 'reserialized'.
input_directory = 'bagValidated'

def validate_export(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit['deposit_uuid']
    outcome = 'success'
    error = ''
    
    path_to_unserialized_deposit = staging_server_common.get_input_path(input_directory, [deposit_uuid, deposit_uuid], 'data')
    try:
        # Determine if we are using articles.xml or issues.xml.
        if os.path.isfile(os.path.join(path_to_unserialized_deposit, 'articles.xml')):
            path_to_export_xml = os.path.join(path_to_unserialized_deposit, 'articles.xml')
        elif os.path.isfile(os.path.join(path_to_unserialized_deposit, 'issues.xml')):
            path_to_export_xml = os.path.join(path_to_unserialized_deposit, 'issues.xml')
        else:
            raise Exception("Can't find export XML file in %s" % (path_to_unserialized_deposit))
            
        # Confirm that the XML file we are validating uses a PKP DTD by reading the
        # first two lines of the file and matching on the DOCTYPE declation.
        num_lines = 2
        xml_file = open(path_to_export_xml)
        for i in range(num_lines):
            line = xml_file.next().strip()
            if i == 1:
                # Test to make sure the DTD is from http://pkp.sfu.ca.
                if not re.match(r'<!DOCTYPE.*PUBLIC.*http://pkp.sfu.ca/.*/dtds', line):
                    raise Exception("Suspicious DOCTYPE definition in export XML file %s: %s" % (path_to_export_xml, line))
        xml_file.close()
        # Validate the XML file and capture any errors.
        try:
            subprocess.check_output(["xmllint", "--noout", "--valid", path_to_export_xml], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            error = e.output
            outcome = 'failure'
    except Exception as e:
        error = error + ' / ' + e.message 
        outcome = 'failure'
    
    finished_on = datetime.now()

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

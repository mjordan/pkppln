"""
Script to check files harvested from OJS journals participating in the 
PKP PLN for viruses.
"""

import os
import sys
import ConfigParser
from datetime import datetime
# http://xael.org/norman/python/pyclamd/
# import pyclamd

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
    # cd = pyclamd.ClamdUnixSocket()
    path_to_unserialized_deposit = staging_server_common.get_input_path(previous_microservice_state, deposit_uuid)
    
    # Write results of the virus check to virus_check.txt in the Bag's /data directory.
    path_to_virus_check_report = path = os.path.join(config.get('Paths', 'processing_root'),
        previous_microservice_state, deposit_uuid, 'virus_check.txt')
        
    f = open(path_to_virus_check_report, 'w')
    for root, _, files in os.walk(path_to_unserialized_deposit):
        for f in files:
            fname = os.path.join(os.getcwd(), root, f)
            # result = cd.scan_file(fname)
            # @todo: Include the virus name if possible.
            if result is None:
                f.write("No virus found: " + fname + "\n")
            else:
                f.write("WARNING: Virus found: " + fname + "\n")
    f.close()

    outcome = 'success'
    error = '' # @todo: check for errors
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

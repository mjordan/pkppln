"""
Script to unzip serialized Bags harvested from OJS journals 
participating in the PKP PLN.
"""

import os
import zipfile
import ConfigParser
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'unzip_deposit_bags'
microservice_state = 'unserialized'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on.
previous_microservice_state = 'payloadVerified'

def unserialize(deposit):
    deposit_uuid = deposit[3]
    deposit_url = deposit[7]
    deposit_filename = staging_server_common.get_deposit_filename(deposit[7])
    error = ''
    started_on = datetime.now()
    
    path_to_input_file = staging_server_common.get_input_path(previous_microservice_state, deposit_uuid, deposit_filename)
    path_to_unserialized_directory = staging_server_common.create_microservice_directory(microservice_state, deposit_uuid)

    zfile = zipfile.ZipFile(path_to_input_file)
    print zfile.namelist()
    # @todo: Check each path in the zip to make sure that none start
    # with '/' or '..'. If they do, stop and issue a warning.
    zfile.extractall(path_to_unserialized_directory)
    
    # @todo: Validate the Bag before updating the db?
    finished_on = datetime.now()
    
    outcome = 'success'
    error = '' # @todo: check for errors
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

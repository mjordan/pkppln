"""
Script to stage Bags containing deposits to the PKP PLN.
"""

import os
import shutil
import ConfigParser
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'stage_deposit_bags'
microservice_state = 'staged'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on.
previous_microservice_state = 'reserialized'

def reserialize_bag(deposit):
    started_on = datetime.now()
    journal_uuid = deposit[5]
    deposit_uuid = deposit[3]
    deposit_filename = staging_server_common.get_deposit_filename(deposit[7])
    outcome = 'success'
    error = '' 
    
    # Don't use deposit_filename here, use normalized reserialzied Bag filename of
    # journal_uuid.issue_uuid.zip
    file_to_stage = journal_uuid + '.' + deposit_uuid + '.zip'
    path_to_input_file = staging_server_common.get_input_path(previous_microservice_state, deposit_uuid, deposit_filename)
    path_to_staged_file = os.path.join(config.get('Paths', 'staging_root'), journal_uuid, file_to_stage)
    try:
        if not os.path.exists(staging_directory):
            os.makedirs(staging_directory)
        shutil.move(path_to_input_file, path_to_staged_file)
    except Exception as e:
        error = e
        outcome = 'failure'
    
    finished_on = datetime.now()
    
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

"""
Script to stage Bags containing deposits to the PKP PLN.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
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
# The name of the directory under the processing root directory. One of
# 'havested', 'bagValidated', or 'reserialized'.
input_directory = 'reserialized'

def stage_bag(deposit):
    started_on = datetime.now()
    journal_uuid = deposit['journal_uuid']
    deposit_uuid = deposit['deposit_uuid']
    deposit_filename = staging_server_common.get_deposit_filename(deposit['deposit_url'])
    outcome = 'success'
    error = '' 
    
    # Don't use deposit_filename here, use normalized reserialzied Bag filename of
    # journal_uuid.issue_uuid.zip
    file_to_stage = '.'.join([deposit['journal_uuid'], deposit['deposit_uuid'], 'tar.gz'])
    path_to_input_file = staging_server_common.get_input_path(input_directory, None, file_to_stage)
    staging_directory = os.path.join(config.get('Paths', 'staging_root'), journal_uuid)
    path_to_staged_file = os.path.join(staging_directory, file_to_stage)
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

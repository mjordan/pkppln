"""
Script to validate Bags harvested from OJS journals 
participating in the PKP PLN.
"""

import os
import bagit
import zipfile
import ConfigParser
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'validate_deposit_bag'
microservice_state = 'bagValidated'
# The name of the directory under the processing root directory. One of
# 'havested', 'unserialized', or 'reserialized'.
input_directory = 'harvested'

def validate_bag(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit['deposit_uuid']
    deposit_url = deposit['deposit_url']
    deposit_filename = staging_server_common.get_deposit_filename(deposit_url)
    outcome = 'success'
    error = ''    
    
    path_to_input_file = staging_server_common.get_input_path(input_directory, [deposit_uuid], deposit_filename)
    path_to_unserialized_directory = staging_server_common.create_microservice_directory(microservice_state, deposit_uuid)

    try:
        zfile = zipfile.ZipFile(path_to_input_file)
        # Check each path in the zip to make sure that none start
        # with '/' or '..'. If they do, stop and issue a warning.
        for name in zfile.namelist():
            if name.startswith('/') or name.startswith('..'):
                raise Exception("Suspicious filename %s in zipped Bag" % (name))
                outcome = 'failure'
        zfile.extractall(path_to_unserialized_directory)
        # Validate the Bag.
        path_to_bag = os.path.join(path_to_unserialized_directory, deposit_uuid)
        try:
            bag = bagit.Bag(path_to_bag)
            if not bag.is_valid():
                error = 'Bag is not valid.'
                outcome = 'failure'
        except Exception as e:
            error = error + ' / ' + e.message 
            outcome = 'failure'
    except Exception as e:
        error = error + ' / ' + e.message 
        outcome = 'failure'

    finished_on = datetime.now()

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

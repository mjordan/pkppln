"""
Script to harvest files from OJS journals identified in SWORD deposits
created by the PKP PLN plugin.
"""

import os
import requests
import ConfigParser
from datetime import datetime

import staging_server_common

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'harvest'
microservice_state = 'harvested'

def harvest(deposit):
    deposit_uuid = deposit[3]
    deposit_filename = staging_server_common.get_deposit_filename(deposit[7])
    error = ''
    started_on = datetime.now()
    
    path_to_harvested_directory = staging_server_common.create_microservice_directory(microservice_state, deposit_uuid)
    path_to_harvested_bag = os.path.join(path_to_harvested_directory, deposit_filename)
    
    print "Path: " + path_to_harvested_bag
    
    # Download the file at deposit_url. We stream it to handle large files gracefully.
    r = requests.get(deposit_url, stream=True)
    with open(path_to_harvested_bag, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
                f.flush()

    finished_on = datetime.now()
    outcome = 'success'
    error = ''
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

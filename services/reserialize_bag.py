"""
Script to 1) add tags to bag-info.txt and 2) reserialize Bags containing OJS
journals participating in the PKP PLN.
"""

import os
import ConfigParser
import bagit
import zipfile
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'reserialize_deposit_bags'
microservice_state = 'reserialized'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on. We use 'unserialized' here instead of
# 'contentVerified' even though the last microservice was 'verify_deposit_structure'.
previous_microservice_state = 'unserialized'

def reserialize_bag(deposit):
    started_on = datetime.now()
    deposit_filename = staging_server_common.get_deposit_filename(deposit[7])
    outcome = 'success'
    error = ''
    # @todo: 1) Add these tags to bag-info.txt: Bagging-Date, External-Description [value of the journal title and issue number],
    # External-Identifier [value of the deposit URL], PKP-PLN-Journal-UUID, PKP-PLN-Deposit-UUID.
    # 2) Add the virus report to the Bag; 3) Reserialize the Bag and assign it a filename using the pattern
    # journaluuid.issueuuid.zip (max 255 chars including extension).
    
    # @todo: add the virus report to the Bag
    # path_to_virus_check_report = path = os.path.join(config.get('Paths', 'processing_root'), previous_microservice_state, deposit_uuid, 'virus_check.txt')    
    
    # @todo: Recreate Bag and serialize it (using .zip) with the deposit filename.
    path_to_unserialized_deposit = staging_server_common.get_input_path(previous_microservice_state, deposit_uuid)
    
    finished_on = datetime.now()

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

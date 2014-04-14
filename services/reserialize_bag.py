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
# knows where to find content to act on.
previous_microservice_state = 'contentVerified'

def reserialize_bag(deposit):
    started_on = datetime.now()
    # @todo: 1) Add these tags to bag-info.txt: Bagging-Date, External-Description [value of the journal title and issue number],
    # External-Identifier [value of the deposit URL], PKP-PLN-Journal-UUID, PKP-PLN-Deposit-UUID.
    # 2) Reserialize the Bag and assign it a filename using the pattern
    # journaluuid.journal_title.issueuuid.zip (max 255 chars including extension).
    
    finished_on = datetime.now()
    
    outcome = 'success'
    error = '' # @todo: check for errors
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

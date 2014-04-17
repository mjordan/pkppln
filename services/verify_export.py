"""
Script to verify OJS export XML, etc. from OJS journals participating in the 
PKP PLN for viruses.
"""

import os
import ConfigParser
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'verify_deposit_structure'
microservice_state = 'contentVerified'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on.
previous_microservice_state = 'virusChecked'

def verify_export(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit[3]
    outcome = 'success'
    error = ''
    
    # @todo: Check for root elements of either <issues> (for issue-level exports) or
    # <articles> (for issue-less journals). Verify this with Chris and James.
    # Then, validate with a call to xmllint (xmllint --noout --valid articles.xml).
    
    finished_on = datetime.now()

    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

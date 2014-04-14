"""
Script to harvest files from OJS journals identified in SWORD deposits
created by the PKP PLN plugin.
"""

from datetime import datetime

import staging_server_common

def harvest(deposit):
    deposit_uuid = deposit[3]
    error = ''
    started_on = datetime.now()
    # @todo: do the actual harvesting.
    print deposit
    finished_on = datetime.now()
    outcome = 'success'
    error = ''
    staging_server_common.update_deposit(deposit_uuid, 'harvested', outcome)
    staging_server_common.log_microservice('harvest', deposit_uuid, started_on, finished_on, outcome, error)

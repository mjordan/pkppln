"""
Script to verify that the reported file size and SHA-1 checksum match
those reported in the SWORD deposit.
"""

import os
import hashlib
import ConfigParser
from datetime import datetime

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'verify_payload'
microservice_state = 'payloadVerified'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on.
previous_microservice_state = 'harvested'

def verify_payload(deposit):
    started_on = datetime.now()
    deposit_uuid = deposit['deposit_uuid']
    reported_sha1_value = deposit['sha1_value']
    reported_deposit_size = deposit['size']
    deposit_filename = staging_server_common.get_deposit_filename(deposit['deposit_url'])
    outcome = 'success'
    
    path_to_input_file = staging_server_common.get_input_path(previous_microservice_state, deposit_uuid, deposit_filename)
    
    # Verify SHA-1 checksum.
    input_file = open(path_to_input_file, 'rb')
    verified_sha1_value = hashlib.sha1()
    while True:
        # Read the file in 10 mb chunks so we don't run out of memory.
        buf = input_file.read(10 * 1024 * 1024)
        if not buf:
            break
        verified_sha1_value.update(buf)
    input_file.close()
    
    sha1_error = ''
    if reported_sha1_value != verified_sha1_value.hexdigest():
        outcome = 'failure'
        sha1_error = 'Reported SHA-1 value of %s differs from verified value of %s' % (reported_sha1_value, verified_sha1_value.hexdigest())
    
    # Get file size.
    filesize_error = ''
    statinfo = os.stat(path_to_input_file)
    if reported_deposit_size != statinfo.st_size:
        outcome = 'failure'
        filesize_error = 'Reported file size of %s differs from verified file size of %s' % (reported_deposit_size, statinfo.st_size)
    
    finished_on = datetime.now()
    
    if (len(sha1_error) or len(filesize_error)):
        error = sha1_error + ' ' + filesize_error
    else:
        error = ''
    staging_server_common.update_deposit(deposit_uuid, microservice_state, outcome)
    staging_server_common.log_microservice(microservice_name, deposit_uuid, started_on, finished_on, outcome, error)

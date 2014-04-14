"""
Script to check files harvested from OJS journals participating in the 
PKP PLN for viruses.
"""

import os
import sys
import ConfigParser
from datetime import datetime
# http://xael.org/norman/python/pyclamd/
# import pyclamd

import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Each microservice must declare a name and a state, for use in the database
# and file paths.
microservice_name = 'check_deposit_for_viruses'
microservice_state = 'virusChecked'
# If this microservice follows another (only the 'harvest' microservice doesn't),
# the previous microservice's state value must be declared as well, so the microservice
# knows where to find content to act on.
previous_microservice_state = 'unserialized'

# cd = pyclamd.ClamdUnixSocket()

for root, _, files in os.walk(sys.argv[1]):
    for f in files:
        fname = os.path.join(os.getcwd(), root, f)
        print "Checking " + fname + " for virus"
        # result = cd.scan_file(fname)
        if result is not None:
            print "WARNING: Virus found: " + fname

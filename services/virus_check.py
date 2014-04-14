"""
Script to check files harvested from OJS journals participating in the 
PKP PLN for viruses.
"""

import os
import sys
# http://xael.org/norman/python/pyclamd/
# import pyclamd

# cd = pyclamd.ClamdUnixSocket()

for root, _, files in os.walk(sys.argv[1]):
    for f in files:
        fname = os.path.join(os.getcwd(), root, f)
        print "Checking " + fname + " for virus"
        # result = cd.scan_file(fname)
        if result is not None:
            print "WARNING: Virus found: " + fname

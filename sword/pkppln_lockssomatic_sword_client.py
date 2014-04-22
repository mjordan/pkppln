#!/usr/bin/env python

"""
Basic SWORD client for use on the PKP PLN staging server. For use
with the LOCKSS-O-Matic SWORD server. Needs further development as
indicated in comments below.

Usage: pkppln_lockssomatic_sword_client.py action depositUUID

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import os 
import sys
import requests
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# @todo: Add server_base_url to the config file.
server_base_url = 'http://lockssomatic.example.com/lockss-o-matic/web/app_dev.php'
# @todo: Get these from the Service Document.
sd_iri = '/api/sword/2.0/sd-iri'
col_iri = '/api/sword/2.0/col-iri/'
cont_iri = '/api/sword/2.0/cont-iri/'

# Bail if no SWORD action is provided.
if (len(sys.argv) < 2):
    print "Sorry, you need to provide a SWORD action: getSD, createDeposit, getStatement or modifyDeposit"
    sys.exit()

# Grab the action from the command line.
action = sys.argv[1]
# In production, this can be hard coded (or put in the config file) to
# be the LOM content provider ID for the PKP PLN Staging Server.
lom_content_provider = sys.argv[2]

# Retrieve Service Document.
if action == 'getSD':
    # Populate the On-Behalf-Of header with the Content Provider's ID.
    headers = {'X-On-Behalf-Of': lom_content_provider}
    print 'Retrieving Service Docuement on behalf of ' + lom_content_provider
    r = requests.get(server_base_url + sd_iri, headers=headers)
    # @todo: Parse service document and get Col-IRI to use in createDeposit.
    print r.content

# Create a deposit.
# curl -v -H "In-Progress: true" --data-binary @atom_create.xml --request POST http://localhost/lockss-o-matic/web/app_dev.php/api/sword/2.0/col-iri/47
if action == 'createDeposit':
    path_to_atom = sys.argv[3]
    # Populate the On-Behalf-Of header with the Content Provider's ID.
    headers = {'X-In-Progress': False}
    # @todo: Write a function to generate the Atom for the current deposit.
    atom = open(path_to_atom, 'rb')
    print 'Creating Deposit on behalf of ' + lom_content_provider
    r = requests.post(server_base_url + col_iri + lom_content_provider, data=atom, headers=headers)
    print r.content
    
# Get SWORD Statement.
# http://localhost/lockss-o-matic/web/app_dev.php/api/sword/2.0/cont-iri/1/1225c695-cfb8-4ebb-aaaa-80da344efa6a/state
if action == 'getStatement':
    # sys.argv[3] will be the UUID of the deposit from the Staging Server.
    content_uuid = sys.argv[3]
    r = requests.get(server_base_url + cont_iri + lom_content_provider + '/' + content_uuid + '/state')
    # @todo: Write a function to parse the Statement and update the deposit's record in the
    # database if state value returned by LOM is 'agreement' for the current deposit.
    print r.content
    
# Modify a deposit.
# curl -v -H "Content-Type: application/xml" -X PUT --data-binary @atom_modify.xml http://localhost/lockss-o-matic/web/app_dev.php/api/sword/2.0/cont-iri/1/1225c695-cfb8-4ebb-aaaa-80da344efa6a/edit
if action == 'modifyDeposit':
    content_uuid = sys.argv[3]
    path_to_atom = sys.argv[4]
    # Populate the On-Behalf-Of header with the Content Provider's ID.
    headers = {'Content-Type': 'application/xml'}
    # @todo: Write a function to generate the Atom for the current deposit with recrawl="false",
    # indicating that LOM should modify the AU configuration so the content journal content is
    # not reharvested.
    atom = open(path_to_atom, 'rb')
    print 'Modifying Deposit on behalf of ' + lom_content_provider
    r = requests.put(server_base_url + cont_iri + lom_content_provider + '/' + content_uuid + '/edit', data=atom, headers=headers)
    print r.status_code

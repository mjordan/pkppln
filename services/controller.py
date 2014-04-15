#!/usr/bin/env python

import sys
import ConfigParser
import MySQLdb as mdb

import staging_server_common
import harvest
import unzip_bag
import virus_check
import verify_export
import reserialize_bag
import stage_bag
import deposit_to_pln

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

# Microservice name is passed in as an argument to the controller.
if len(sys.argv) == 2:
    microservice = sys.argv[1]
else:
    sys.exit('PKP PLN staging server microservices controller called with no argument')

"""
Calls to microservices. Each microservice consumes entries in the 'deposits'
table with a specific 'state' value, and updates the state value so that the
next microservice can identify the deposit for consumption.
"""

# Harvest: needs state 'depositedByJournal', sets state to 'harvested'
if microservice == 'harvest_deposits':
    deposits = staging_server_common.get_deposits('depositedByJournal')
    if deposits:
        for deposit in deposits:
            harvest.harvest(deposit)

# Unserialize Bags: needs state 'harvested', sets state to 'unserialized'
elif microservice == 'unzip_deposit_bags':
    deposits = staging_server_common.get_deposits('harvested')
    if deposits:
        for deposit in deposits:
            unzip_bag.unserialize(deposit)

# Check for viruses: needs state 'unserialized', sets state to 'virusChecked'
elif microservice == 'check_deposit_for_viruses':
    deposits = staging_server_common.get_deposits('unserialized')
    if deposits:
        for deposit in deposits:
            virus_check.check(deposit)

# Verify deposit structure: needs state 'virusChecked', sets state to 'contentVerified'
elif microservice == 'verify_deposit_structure':
    deposits = staging_server_common.get_deposits('virusChecked')
    if deposits:
        for deposit in deposits:
            verify_export.verify_export(deposit)

# Reserialize Bags: needs state 'contentVerified', sets state to 'reserialized'
elif microservice == 'reserialize_deposit_bags':
    deposits = staging_server_common.get_deposits('contentVerified')
    if len(deposits):
        for deposit in deposits:
            reserialize_bag.reserialize_bag(deposit)
    
# Stage Bags: needs state 'reserialized', sets state to 'staged'
elif microservice == 'stage_deposit_bags':
    deposits = staging_server_common.get_deposits('reserialized')
    if len(deposits):
        for deposit in deposits:
            stage_bag.stage_bag(deposit)

# Deposit to the PLN: needs state 'staged', sets state to 'depositedToPln'
elif microservice == 'deposit_to_pln':
    deposits = staging_server_common.get_deposits('staged')
    if deposits:
        for deposit in deposits:
            deposit_to_pln.deposit_to_pln(deposit)
    
# State request against LOM handled as a separate cron job.
    
else:
    sys.exit('PKP PLN staging server microservices controller called with invalid arguement' % sys.argv[1])









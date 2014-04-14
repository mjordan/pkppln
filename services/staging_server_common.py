"""
Functions shared by PKP PLN microservices.
"""

import sys
import os
import ConfigParser
import MySQLdb as mdb

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

def get_deposits(state):
    print state
    # Get the deposits that have the indicated state value
    # and return them to the microservice for processing.
    con = mdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
        config.get('Database', 'db_password'), config.get('Database', 'db_name'))
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM deposits WHERE state = %s AND outcome = 'success'", state)
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    print cur.rowcount
    if cur.rowcount:
        deposits = []
        for row in cur:
            deposits.append(row)
        return deposits

def update_deposit(deposit_uuid, state, outcome):
    con = mdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
        config.get('Database', 'db_password'), config.get('Database', 'db_name'))
    try:
        with con:
            cur = con.cursor()
            cur.execute("UPDATE deposits SET state = %s, outcome = %s WHERE deposit_uuid = %s",
                (state, outcome, deposit_uuid))
            # @todo: check to make sure cur.rowcount == 1.
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

def log_microservice(microservice, deposit_uuid, started_on, finished_on, outcome, error):
    con = mdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
        config.get('Database', 'db_password'), config.get('Database', 'db_name'))
    try:
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO microservices " +
                "(microservice, deposit_uuid, started_on, finished_on, outcome, error) " +
                "VALUES(%s, %s, %s, %s, %s, %s)", (microservice, deposit_uuid, started_on,
                finished_on, outcome, error))            
            # @todo: check to make sure cur.rowcount == 1.
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

def create_microservice_directory(microservice_state, deposit_uuid):
    # @todo: Wrap in a try/except.
    path_to_directory = os.path.join(config.get('Paths', 'processing_root'), microservice_state, deposit_uuid)
    if not os.path.exists(path_to_directory):
        os.makedirs(path_to_directory)
    return path_to_directory
    
def get_input_path(previous_microservice_state, deposit_uuid, deposit_filename=None):
    if deposit_filename is None:
        path = os.path.join(config.get('Paths', 'processing_root'), previous_microservice_state, deposit_uuid)
    else:
        path = os.path.join(config.get('Paths', 'processing_root'), previous_microservice_state, deposit_uuid, deposit_filename)
    return path

def get_deposit_filename(url):
    return url.split('/')[-1]

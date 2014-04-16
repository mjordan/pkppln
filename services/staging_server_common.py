"""
Functions shared by PKP PLN microservices.
"""

import sys
import os
import logging
import logging.handlers
import ConfigParser
import MySQLdb

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

logger = logging.getLogger()
# Create error file handler and set level to error.
file_handler = logging.FileHandler(config.get('Paths', 'error_log'),"w")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Create email handler and set level to error.
smtp_handler = logging.handlers.SMTPHandler(mailhost="localhost",
                                            fromaddr="mjordan@sfu.ca", 
                                            toaddrs=config.get('Paths', 'error_email'),
                                            subject="Database error in PKP PLN staging server")
smtp_handler.setLevel(logging.ERROR)
logger.addHandler(smtp_handler)

def get_deposits(state):
    print state
    # Get the deposits that have the indicated state value
    # and return them to the microservice for processing.
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("SELECT * FROM deposits WHERE state = %s AND outcome = 'success'", state)
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        logging.exception(e)
        sys.exit(1)
    print cur.rowcount
    if cur.rowcount:
        deposits = []
        for row in cur:
            deposits.append(row)
        return deposits

def update_deposit(deposit_uuid, state, outcome):
    print "State from update_deposit is " + state
    print "Outcome from update_deposit is " + outcome
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("UPDATE deposits SET state = %s, outcome = %s WHERE deposit_uuid = %s",
            (state, outcome, deposit_uuid))
        con.commit()
        # @todo: check to make sure cur.rowcount == 1 and not 0.
        print "Just executed update_deposit"
        print "Number of rows updated: %d" % cur.rowcount
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        logging.exception(e)
        sys.exit(1)

def log_microservice(microservice, deposit_uuid, started_on, finished_on, outcome, error):
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("INSERT INTO microservices " +
            "(microservice, deposit_uuid, started_on, finished_on, outcome, error) " +
            "VALUES(%s, %s, %s, %s, %s, %s)", (microservice, deposit_uuid, started_on,
            finished_on, outcome, error))
        con.commit()
        # @todo: check to make sure cur.rowcount == 1 and not 0.
        print "Just executed log_microservice"
        print "Number of rows updated: %d" % cur.rowcount
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        logging.exception(e)
        sys.exit(1)

def create_microservice_directory(microservice_state, deposit_uuid):
    # @todo: Wrap in a try/except and log/email error.
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

"""
Functions shared by PKP PLN microservices, plus most database functions.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import sys
import os
import logging
import logging.handlers
from datetime import datetime
import ConfigParser
import MySQLdb
import MySQLdb.cursors

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
smtp_handler = logging.handlers.SMTPHandler(
    mailhost=config.get('Email', 'error_email_mailhost'),
    fromaddr=config.get('Email', 'error_email_fromaddr'), 
    toaddrs=config.get('Email', 'error_email_toaddrs'),
    subject=config.get('Email', 'error_email_subject'))
smtp_handler.setLevel(logging.ERROR)
logger.addHandler(smtp_handler)

def get_deposits(processing_state):
    print "Debug: Processing state is " + processing_state
    # Get the deposits that have the indicated processing state value
    # and return them to the microservice for processing.
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'),
            cursorclass=MySQLdb.cursors.DictCursor)
        cur = con.cursor()
        cur.execute("SELECT * FROM deposits WHERE processing_state = %s AND outcome = 'success'", processing_state)
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

def insert_deposit(action, email, deposit_uuid, on_behalf_of, checksum_value, url, processing_size, state, outcome):
    con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO deposits " +
            "(action, contact_email, deposit_uuid, date_deposited, journal_uuid, \
              sha1_value, deposit_url, size, processing_state, outcome, harvested, pln_state, deposited_lom) " +
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (action, email, deposit_uuid,
             datetime.now(), on_behalf_of, checksum_value, url, size, processing_state, outcome, None, 'in_progress', None))
        con.commit()
        return True # Do we need this?
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        logging.exception(e)
        sys.exit(1)

def insert_journal(journal_uuid, title, issn, email, deposit_uuid):
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("INSERT INTO journals " +
            "(journal_uuid, title, issn, contact_email, deposit_uuid, date_deposited) " +
            "VALUES(%s, %s, %s, %s, %s, %s)", (journal_uuid, title, issn, email, deposit_uuid, datetime.now()))
        con.commit()
        # @todo: check to make sure cur.rowcount == 1 and not 0.
    except MySQLdb.Error, e:
        # print "Error %d: %s" % (e.args[0],e.args[1])
        logging.exception(e)
        sys.exit(1)

def update_deposit(deposit_uuid, processing_state, outcome):
    print "State from update_deposit is " + processing_state
    print "Outcome from update_deposit is " + outcome
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("UPDATE deposits SET processing_state = %s, outcome = %s WHERE deposit_uuid = %s",
            (processing_state, outcome, deposit_uuid))
        con.commit()
        # @todo: check to make sure cur.rowcount == 1 and not 0.
    except MySQLdb.Error, e:
        # print "Error %d: %s" % (e.args[0],e.args[1])
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
    except MySQLdb.Error, e:
        # print "Error %d: %s" % (e.args[0],e.args[1])
        logging.exception(e)
        sys.exit(1)

def create_microservice_directory(microservice_state, deposit_uuid):
    try:
        path_to_directory = os.path.join(config.get('Paths', 'processing_root'), microservice_state, deposit_uuid)
        if not os.path.exists(path_to_directory):
            os.makedirs(path_to_directory)
        return path_to_directory
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
    
def get_input_path(input_directory, dirs, deposit_filename=None):
    if dirs is None:
        intermediate_path = ''
    else:
        intermediate_path = os.sep.join(dirs)

    if deposit_filename is None:
        path = os.path.join(config.get('Paths', 'processing_root'), input_directory, intermediate_path)
    else:
        path = os.path.join(config.get('Paths', 'processing_root'), input_directory, intermediate_path, deposit_filename)
    return path

def get_deposit_filename(url):
    return url.split('/')[-1]

import sys
import os
import hashlib
import logging
import logging.handlers
from datetime import datetime
import ConfigParser
import MySQLdb
import MySQLdb.cursors
from os.path import abspath, dirname
import xml.etree.ElementTree as element_tree
from xml.etree.ElementTree import Element, SubElement


config_file_name = 'config.cfg'
namespaces = {
    'entry': 'http://www.w3.org/2005/Atom',
    'pkp': 'http://pkp.sfu.ca/SWORD',
    'dcterms': 'http://purl.org/dc/terms/'
}


def __config():
    """
    Get a configuration object for the application.
    """
    config_path = dirname(abspath(__file__)) + '/' + config_file_name
    config = ConfigParser.ConfigParser()
    success = config.read(config_path)
    if config_path not in success:
        raise Exception('Cannot load config file ' + config_path)
    return config

_config = None


def get_config():
    global _config
    if _config is None:
        _config = __config()
    return _config


def __connect():
    """
    Connect to the database and return a database connection. You must
    get the cursor manually. Autocommit is not enabled.
    """
    config = get_config()
    con = MySQLdb.connect(
        host=config.get('Database', 'db_host'),
        user=config.get('Database', 'db_user'),
        passwd=config.get('Database', 'db_password'),
        db=config.get('Database', 'db_name'),
        cursorclass=MySQLdb.cursors.DictCursor,
        use_unicode=True,
        charset="utf8"
    )
    return con

_mysql = None


def get_connection():
    global _mysql
    if _mysql is None:
        _mysql = __connect()
    return _mysql


def get_deposits(state):
    # Get the deposits that have the indicated processing state value
    # and return them to the microservice for processing.
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute("""
        SELECT * FROM deposits WHERE processing_state = %s
        AND outcome = 'success' OR outcome = 'forced'; """, [state])
    except MySQLdb.Error, e:
        logging.exception(e)
        sys.exit(1)
    return cursor.fetchall()


def update_deposit(deposit_uuid, state, result):
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute("""
        UPDATE deposits SET
        processing_state = %s, outcome = %s WHERE deposit_uuid = %s""",
                       [state, result, deposit_uuid])
        # @todo: check to make sure cursor.rowcount == 1 and not 0.
    except MySQLdb.Error, e:
        mysql.rollback()
        logging.exception(e)
        sys.exit(1)
    mysql.commit()


def get_journal_info(uuid):
    """
    Query information about the journal that produced this deposit and wrap it
    in XML to include in the Bag.
    """
    mysql = get_connection()
    cursor = mysql.cursor()

    cursor.execute("SELECT * FROM journals WHERE deposit_uuid = %s", [uuid])

    if cursor.rowcount:
        element_tree.register_namespace('pkp', 'http://pkp.sfu.ca/SWORD')
        journal = Element('{http://pkp.sfu.ca/SWORD}journal')
        for row in cursor.fetchall():
            for key in row:
                foo = SubElement(journal, 'pkp:' + key)
                if key == 'date_deposited':
                    value = row[key].strftime('%Y-%m-%d')
                else:
                    value = row[key]
                foo.text = str(value)
        return element_tree.tostring(journal)


def deposit_filename(url):
    return url.split('/')[-1]


def file_sha1(filepath):
    input_file = open(filepath, 'rb')
    calculated_sha1 = hashlib.sha1()
    while True:
        # Read the filename in 10 mb chunks so we don't run out of memory.
        buf = input_file.read(10 * 1024 * 1024)
        if not buf:
            break
        calculated_sha1.update(buf)
    input_file.close()
    return calculated_sha1.hexdigest()


def input_path(in_dir, dirs='', filename=''):
    config = get_config()
    processing_root = config.get('Paths', 'processing_root')
    tmp_path = os.sep.join(dirs)
    path = os.path.join(processing_root, in_dir, tmp_path, filename)
    return path


def microservice_directory(state, uuid):
    config = get_config()
    try:
        processing_root = config.get('Paths', 'processing_root')
        path = os.path.join(processing_root, state, uuid)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    except Exception as exception:
        logging.exception(exception)
        sys.exit(1)

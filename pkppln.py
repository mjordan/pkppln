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
    'dcterms': 'http://purl.org/dc/terms/',
    'sword': 'http://purl.org/net/sword/',
    'app': 'http://www.w3.org/2007/app',
    'lom': 'http://lockssomatic.info/SWORD2',
}


def __config():
    """
    Parse the config file and return the result.
    """
    config_path = dirname(abspath(__file__)) + '/' + config_file_name
    config = ConfigParser.ConfigParser()
    success = config.read(config_path)
    if config_path not in success:
        raise Exception('Cannot load config file ' + config_path)
    return config

_config = None


def get_config():
    """
    Get a configuration object for the application.
    """
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


def __request_logger():
    config = get_config()
    logging.basicConfig(
        filename=config.get('Paths', 'error_log'),
        level=logging.INFO,
        format=logging.BASIC_FORMAT
    )

    logger = logging.getLogger('pkppln_requests')
    logger.setLevel(logging.INFO)
    log_filehandle = logging.FileHandler(config.get('Paths', 'request_log'))
    log_filehandle.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s\t%(message)s')
    log_filehandle.setFormatter(log_formatter)
    logger.addHandler(log_filehandle)
    return logger

_logger = None


def get_logger():
    global _logger
    if _logger is None:
        _logger = __request_logger()
    return _logger


def log_message(message, level=logging.INFO):
    logger = get_logger()
    logger.log(level, message)


def check_access(uuid):
    config = get_config()
    # whitelist.txt and blacklist.txt contain journal UUIDs to allow or block,
    # respectively, one UUID per line. If the files don't exist, we define
    # sensible default values for the lists.

    # Get the SWORD-server level value of accepting_deposits. If this is set to
    # 'No', don't bother checking the white or black lists.
    accepting = config.get('Deposits', 'pln_accept_deposits')
    if accepting == 'No':
        return 'No'

    if os.path.exists(config.get('Deposits', 'pln_accept_deposits_whitelist')):
        whitelist = [line.strip() for line in open(
            config.get('Deposits', 'pln_accept_deposits_whitelist'))]
    else:
        whitelist = ['all']

    if os.path.exists(config.get('Deposits', 'pln_accept_deposits_blacklist')):
        blacklist = [line.strip() for line in open(
            config.get('Deposits', 'pln_accept_deposits_blacklist'))]
    else:
        blacklist = []

    # 'Yes' or 'No' gets inserted into the <pkp:pln_accepting> element in the
    # service document; the create and update deposit calls also check.
    if (uuid in whitelist or whitelist[0] == 'all') and uuid not in blacklist:
        return 'Yes'
    else:
        return 'No'


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


def insert_deposit(action, deposit_uuid, deposit_volume, deposit_issue,
                   deposit_pubdate, on_behalf_of, checksum_value, url, size,
                   processing_state, outcome):
    """
    Insert a deposit record to the database. Does not do a rollback() on
    failure or a commit() on success - that is the repsonsibility of the
    caller.
    """
    try:
        cursor = get_connection().cursor()
        cursor.execute("""
        INSERT INTO deposits (action, deposit_uuid, deposit_volume,
        deposit_issue, deposit_pubdate, date_deposited, journal_uuid,
        sha1_value, deposit_url, size, processing_state, outcome, pln_state)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (action, deposit_uuid, deposit_volume, deposit_issue,
                        deposit_pubdate, datetime.now(), on_behalf_of,
                        checksum_value, url, size, processing_state, outcome,
                        'in_progress'))
    except MySQLdb.Error as exception:
        logging.exception(exception)
        return False
    if cursor.rowcount == 1:
        return True
    else:
        return False
    return True


def insert_journal(journal_uuid, title, issn, journal_url, email,
                   deposit_uuid):
    """
    Insert a journal record to the database. Does not do a rollback() on
    failure or a commit() on success - that is the repsonsibility of the
    caller.
    """
    cursor = get_connection().cursor()
    try:
        cursor.execute("""
        INSERT INTO journals (journal_uuid, title, issn, journal_url,
        contact_email, deposit_uuid, date_deposited)
        VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                       (journal_uuid, title, issn, journal_url, email,
                        deposit_uuid, datetime.now()))
    except MySQLdb.Error as e:
        logging.exception(e)
        return False
    if cursor.rowcount == 1:
        return True
    else:
        return False


def get_journal(uuid):
    mysql = get_connection()
    cursor = mysql.cursor()

    cursor.execute("SELECT * FROM journals WHERE deposit_uuid = %s", [uuid])
    if cursor.rowcount:
        return cursor.fetchall()[0]
    return None


def get_journal_xml(uuid):
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


def file_md5(filepath):
    input_file = open(filepath, 'rb')
    calculated_md5 = hashlib.md5()
    while True:
        # Read the filename in 10 mb chunks so we don't run out of memory.
        buf = input_file.read(10 * 1024 * 1024)
        if not buf:
            break
        calculated_md5.update(buf)
    input_file.close()
    return calculated_md5.hexdigest()


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

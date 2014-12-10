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

"""
Common functions for the PKP PLN staging server.
"""

"""
Set pkppln.config_file_name to something else before calling get_config()
for testing.
"""
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
    Parse the config file and return the result. Internal use only.
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
    get the cursor manually. Autocommit is not enabled. Internal use only.
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
    """
    Connect to the database and return a database connection. You must
    get the cursor manually. Autocommit is not enabled.
    """
    global _mysql
    if _mysql is None:
        _mysql = __connect()
    return _mysql


def __request_logger():
    """Get a logging object. Internal use only."""
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
    """Get a logging object."""
    global _logger
    if _logger is None:
        _logger = __request_logger()
    return _logger


def log_message(message, level=logging.INFO):
    """Log a message, with optional logging level."""
    logger = get_logger()
    logger.log(level, message)


def check_access(uuid):
    """Check access to the PLN for a journal UUID.
 * If the config file is not accepting, then never accept.
 * If there is no whitelist file, then all uuids are whitelisted.
 * If there is a whitelist file, then the uuid must be listed in the file.
 * If there is no blacklist file, then no uuids are blacklisted.
 * If there is a blacklist file, then the uuid must not be listed there.

 The whitelist and blacklist files are not required to exist. Lines in
 those files which start with a semicolon or are blank are ignored.
"""
    config = get_config()
    # whitelist.txt and blacklist.txt contain journal UUIDs to allow or block,
    # respectively, one UUID per line. If the files don't exist, we define
    # sensible default values for the lists.

    # Get the SWORD-server level value of accepting_deposits. If this is set to
    # 'No', don't bother checking the white or black lists.
    accepting = config.get('Deposits', 'pln_accept_deposits')
    if accepting == 'No':
        return 'No'

    whitelist_path = config.get('Deposits', 'pln_accept_deposits_whitelist')
    if os.path.exists(whitelist_path):
        whitelist = [w.strip() for w in tuple(open(whitelist_path))
                     if not w.startswith(';') and w != '\n'
                     ]
    else:
        whitelist = ['all']

    blacklist_path = config.get('Deposits', 'pln_accept_deposits_blacklist')
    if os.path.exists(blacklist_path):
        blacklist = [w.strip() for w in tuple(open(blacklist_path))
                     if not w.startswith(';') and w != '\n'
                     ]
    else:
        blacklist = []

    # 'Yes' or 'No' gets inserted into the <pkp:pln_accepting> element in the
    # service document; the create and update deposit calls also check.
    if (uuid in whitelist or whitelist[0] == 'all') and uuid not in blacklist:
        return 'Yes'
    else:
        return 'No'


def get_deposit(uuid):
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute('SELECT * FROM DEPOSITS WHERE deposit_uuid=%s', [uuid])
    except MySQLdb.Error, e:
        logging.exception(e)
        sys.exit(1)
    return cursor.fetchone()


def get_deposits(state):
    """
    Get the deposits that have the indicated processing state value
    and return them to the microservice for processing.
    """
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute("""
        SELECT * FROM deposits WHERE processing_state = %s
        AND outcome='success' OR outcome='forced' OR outcome='reset'
        """, [state])
    except MySQLdb.Error, e:
        logging.exception(e)
        sys.exit(1)
    return cursor.fetchall()


def update_deposit(deposit_uuid, state, result):
    """
    Update a deposit in the database. Does not do a commit or rollback. The
    caller must decide to commit or rollback the transaction.
    """
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute("""
        UPDATE deposits SET
        processing_state = %s, outcome = %s
        WHERE deposit_uuid = %s""",
                       [state, result, deposit_uuid])
        # @todo: check to make sure cursor.rowcount == 1 and not 0.
    except MySQLdb.Error as exception:
        logging.exception(exception)
        return False
    if cursor.rowcount == 1:
        return True
    else:
        return False


def record_deposit(deposit, receipt):
    """Successfully sent deposit to lockssomatic. Record the receipt."""
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute("""
        UPDATE deposits SET
        deposit_receipt = %s
        WHERE deposit_uuid = %s""",
                       [receipt, deposit['deposit_uuid']])
        # @todo: check to make sure cursor.rowcount == 1 and not 0.
    except MySQLdb.Error as exception:
        logging.exception(exception)
        return False
    return True


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
    return True


def log_microservice(service, uuid, start_time, end_time, result, error):
    """Log the service action ot the database."""
    mysql = get_connection()
    cursor = mysql.cursor()
    try:
        cursor.execute("""
        INSERT INTO microservices (microservice, deposit_uuid, started_on,
        finished_on, outcome, error) VALUES(%s, %s, %s, %s, %s, %s)""",
                       [service, uuid, start_time, end_time,
                        result, error])
    except MySQLdb.Error as mysql_error:
        logging.exception(mysql_error)
        return False
    return True


def get_journal(uuid):
    """Get a journal from the database and return it."""
    mysql = get_connection()
    cursor = mysql.cursor()

    cursor.execute("SELECT * FROM journals WHERE deposit_uuid = %s", [uuid])
    if cursor.rowcount:
        return cursor.fetchone()
    return None


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


def get_journal_xml(uuid):
    """
    Query information about the root that produced this deposit and wrap it
    in XML to include in the Bag.
    """

    journal = get_journal(uuid)
    if journal is not None:
        element_tree.register_namespace('pkp', 'http://pkp.sfu.ca/SWORD')
        root = Element('{http://pkp.sfu.ca/SWORD}root')
        for key in journal:
            element = SubElement(root, 'pkp:' + key)
            if key == 'date_deposited':
                value = journal[key].strftime('%Y-%m-%d')
            else:
                value = journal[key]
            element.text = str(value)
        return element_tree.tostring(root)


def deposit_filename(url):
    """Determine the filename of a deposit from the URL from which it was
    harvested."""
    return url.split('/')[-1]


def file_sha1(filepath):
    """Calculate a sha1 checksum for a file."""
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
    """Calculate an md5 checksum for a file."""
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
    """Calculate an input directory based on the config file and
    any additional information.

    pkppln.input_path('processing_root', ['a', 'b'], 'foo.txt')
    """
    config = get_config()
    processing_root = config.get('Paths', 'processing_root')
    tmp_path = os.sep.join(dirs)
    path = os.path.join(processing_root, in_dir, tmp_path, filename)
    return path


def microservice_directory(state, uuid):
    """Find or create the directory for the microservice to work."""
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

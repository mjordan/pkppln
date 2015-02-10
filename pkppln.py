import sys
import os
import hashlib
import logging
import logging.handlers
from datetime import datetime
import ConfigParser
import MySQLdb
import MySQLdb.cursors
from os.path import abspath, dirname, getmtime
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
config_path = dirname(abspath(__file__)) + '/' + config_file_name
namespaces = {
    'entry': 'http://www.w3.org/2005/Atom',
    'pkp': 'http://pkp.sfu.ca/SWORD',
    'dcterms': 'http://purl.org/dc/terms/',
    'sword': 'http://purl.org/net/sword/',
    'app': 'http://www.w3.org/2007/app',
    'lom': 'http://lockssomatic.info/SWORD2',
    'oph': 'http://www.editeur.org/onix/serials/SOH',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}


def __config():
    """
    Parse the config file and return the result. Internal use only.
    """
    config = ConfigParser.ConfigParser()
    success = config.read(config_path)
    if config_path not in success:
        raise Exception('Cannot load config file ' + config_path)
    return config

_config = None
_dbconn = None
_logger = None
_config_mtime = None


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


def get_connection():
    """
    Connect to the database and return a database connection. You must
    get the cursor manually. Autocommit is not enabled.
    """
    global _dbconn
    if _dbconn is None:
        _dbconn = __connect()

    try:
        _dbconn.ping(True)
    except (AttributeError, MySQLdb.OperationalError):
        _dbconn = __connect()

    return _dbconn


def __request_logger():
    """Get a logging object. Internal use only."""
    config = get_config()
    logger = logging.getLogger('pkppln_log')
    logger.setLevel(logging.INFO)
    log_filehandle = logging.FileHandler(
        config.get('Paths', 'log_file'))
    log_filehandle.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_filehandle.setFormatter(log_formatter)
    logger.addHandler(log_filehandle)
    return logger


# -----------------------------------------------------------------------------


def initialize():
    """If the config file has been modified since the last time it was read
    then reset the _config, _dbconn, and _logger variables. This will force
    them to be recreated on the next call to get_config(), get_connection(),
    or get_logger()."""
    global _config_mtime, _config, _dbconn, _logger
    if _config_mtime is None or _config_mtime < getmtime(config_path):
        _config_mtime = getmtime(config_path)
        _config = None
        _dbconn = None
        _logger = None


# -----------------------------------------------------------------------------


# @TODO use a separate error logger.
def get_logger():
    """Get a logging object."""
    global _logger
    if _logger is None:
        _logger = __request_logger()
    return _logger


def log_message(message, level=logging.INFO):
    """Log a message, with optional logging level."""
    get_logger().log(level, message)


# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------


def db_query(sql, params=None):
    mysql = get_connection()
    cursor = mysql.cursor()
    if params is None:
        params = []
    try:
        cursor.execute(sql, params)
    except MySQLdb.Error as exception:
        log_message('Database error: {}'.format(exception), logging.CRITICAL)
        sys.exit(1)
    return cursor.fetchall()


def db_execute(sql, params=None):
    mysql = get_connection()
    cursor = mysql.cursor()
    if params is None:
        params = []
    try:
        cursor.execute(sql, params)
    except MySQLdb.Error as exception:
        log_message('Database error: {}'.format(exception), logging.CRITICAL)
        sys.exit(1)
    return cursor.rowcount


def db_commit():
    mysql = get_connection()
    mysql.commit()


# -----------------------------------------------------------------------------


def get_term_languages():
    languages = db_query("""
            SELECT distinct(lang_code) FROM terms_of_use ORDER BY lang_code;
        """)
    if len(languages) == 0:
        log_message(
            'found no terms of use languages.',
            logging.CRITICAL
        )
        sys.exit(1)
    return languages


def get_term_keys():
    key_codes = db_query("""
            SELECT distinct(key_code) FROM terms_of_use ORDER BY key_code;
        """)
    if len(key_codes) == 0:
        log_message(
            'found no terms of use key codes.',
            logging.CRITICAL
        )
        sys.exit(1)
    return key_codes


def get_term(key_code, lang_code='en-us'):
    if isinstance(key_code, dict):
        code = key_code['key_code']
    else:
        code = key_code

    terms = db_query("""
        SELECT * FROM terms_of_use WHERE lang_code = %s AND key_code = %s
        ORDER BY id DESC
        LIMIT 1
        """, [lang_code.lower(), code])
    if len(terms) == 1:
        return terms[0]
    return None


def get_all_terms(language='en-us'):
    key_codes = get_term_keys()
    terms = []
    for key_code in key_codes:
        term = get_term(key_code, language)
        if term is None:
            if language == 'en-us':
                log_message(
                    'Cannot find term ' + key_code + ' in en-US',
                    logging.CRITICAL
                )
                sys.exit(1)
            else:
                log_message(
                    'Cannot find term '
                    + key_code['key_code'] + ' in ' + language,
                    logging.WARN
                )
                term = get_term(key_code)
        terms.append(term)
    terms.sort(key=lambda t: int(t['weight']))
    return terms


def get_terms_key(key_code):
    if isinstance(key_code, dict):
        code = key_code['key_code']
    else:
        code = key_code
    terms = db_query("""
        SELECT * FROM terms_of_use WHERE key_code = %s
        """, [code])
    if len(terms) > 0:
        return terms
    return None


def edit_term(term):
    result = db_execute("""
        INSERT INTO terms_of_use (weight, key_code, lang_code, content)
        VALUES(%s, %s, %s, %s)""",  [
        term['weight'], term['key_code'], term['lang_code'],
        term['content']
    ])
    if result == 1:
        db_commit()
        return True
    else:
        return False


def update_term(term):
    """Minor change - don't insert a new version of the term."""
    result = db_execute("UPDATE terms_of_use SET weight = %s WHERE id = %s", [
        term['weight'], term['id']
    ])
    if result == 1:
        db_commit()
        return True
    else:
        return False

# -----------------------------------------------------------------------------


def get_deposit(uuid):
    return db_query('SELECT * FROM DEPOSITS WHERE deposit_uuid=%s', [uuid])


def get_deposits(state):
    """
    Get the deposits that have the indicated processing state value
    and return them to the microservice for processing.
    """
    return db_query("""
        SELECT * FROM deposits
        WHERE processing_state = %s AND outcome <> 'failed'
        """, [state])


def update_deposit(deposit_uuid, state, result):
    """
    Update a deposit in the database. Does not do a commit or rollback. The
    caller must decide to commit or rollback the transaction.
    """
    result = db_execute("""
        UPDATE deposits SET
        processing_state = %s, outcome = %s
        WHERE deposit_uuid = %s""",
                        [state, result, deposit_uuid])
    if result == 1:
        return True
    else:
        return False


def record_deposit(deposit, receipt):
    """Successfully sent deposit to lockssomatic. Record the receipt. Does not
    do a commit or rollback. The caller must decide to commit or rollback
    the transaction."""
    result = db_execute("""
        UPDATE deposits SET
        deposit_receipt = %s
        WHERE deposit_uuid = %s""",
                        [receipt, deposit['deposit_uuid']])
    if result == 1:
        return True
    else:
        return False


def insert_deposit(deposit_uuid, journal_uuid, deposit_action,
                   deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1,
                   deposit_url, deposit_size, processing_state, outcome):
    """
    Insert a deposit record to the database. Does not do a rollback() on
    failure or a commit() on success - that is the repsonsibility of the
    caller.
    """
    result = db_execute("""
        INSERT INTO deposits (deposit_uuid, journal_uuid, deposit_action,
        deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1,
        deposit_url, deposit_size, processing_state, outcome, pln_state)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        [deposit_uuid, journal_uuid, deposit_action,
                         deposit_volume, deposit_issue, deposit_pubdate,
                         deposit_sha1, deposit_url, deposit_size,
                         processing_state, outcome, "inProgress"
                         ])
    if result == 1:
        return True
    else:
        return False


# -----------------------------------------------------------------------------


def get_journal_deposits(journal_uuid, state):
    """
    Get the deposits that have the indicated processing state value
    and return them to the microservice for processing.
    """
    return db_query("""
        SELECT * FROM deposits WHERE journal_uuid = %s AND
        processing_state = %s AND outcome <> 'failed'
        """, [journal_uuid, state])


def get_journal(uuid):
    journals = db_query("SELECT * FROM journals WHERE journal_uuid = %s",
                        [uuid])
    if len(journals) == 0:
        return None
    if len(journals) == 1:
        return journals[0]
    log_message('Multiple journal records with UUID ' + uuid, logging.CRITICAL)


def insert_journal(journal_uuid, title, issn, journal_url, contact_email,
                   publisher_name, publisher_url):
    """
    Insert a journal record to the database. Does not do a rollback() on
    failure or a commit() on success - that is the repsonsibility of the
    caller.
    """
    result = db_execute("""
        INSERT INTO journals (journal_uuid, title, issn, journal_url,
        contact_email, publisher_name, publisher_url)
        VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                        [journal_uuid, title, issn, journal_url, contact_email,
                         publisher_name, publisher_url])
    if result == 1:
        return True
    else:
        return False


def get_journals():
    """Get all distinct journals from the database, sorted by title"""
    return db_query('''
        select title, journal_url, publisher_name, publisher_url, issn,
            max(date_deposited) as recent_deposit, journal_uuid
        from journals
        group by title, journal_url, journal_uuid, issn, publisher_name, publisher_url
        order by title, journal_url, journal_uuid, issn, publisher_name, publisher_url
        ''')


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


# -----------------------------------------------------------------------------


def log_microservice(service, uuid, start_time, end_time, result, error):
    """Log the service action ot the database."""
    result = db_execute("""
        INSERT INTO microservices (microservice, deposit_uuid, started_on,
        finished_on, outcome, error) VALUES(%s, %s, %s, %s, %s, %s)""",
                        [service, uuid, start_time, end_time,
                         result, error])
    db_commit()


# -----------------------------------------------------------------------------


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

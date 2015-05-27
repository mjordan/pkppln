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
import warnings
import pytz

warnings.filterwarnings('error', category=MySQLdb.Warning)


class PlnError(Exception):

    """General purpose error exception."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        try:
            return repr(self.value)
        except:
            pass
        try:
            value = unicode(self.value)
            return value.encode("ascii", "backslashreplace")
        except:
            pass
        return '<unprintable %s object>' % type(self.value).__name__


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
    'sword': 'http://purl.org/net/sword/terms/',
    'app': 'http://www.w3.org/2007/app',
    'lom': 'http://lockssomatic.info/SWORD2',
    'oph': 'http://www.editeur.org/onix/serials/SOH',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}


_config = None
_logger = None
_config_mtime = None


# -----------------------------------------------------------------------------

def config_path():
    return dirname(abspath(__file__)) + '/' + config_file_name


def initialize():
    """If the config file has been modified since the last time it was read
    then reset the _config, _dbconn, and _logger variables. This will force
    them to be recreated on the next call to get_config(), get_connection(),
    or get_logger()."""
    global _config_mtime, _config, _logger
    if _config_mtime is None or _config_mtime < getmtime(config_path()):
        _config_mtime = getmtime(config_path())
        _config = None
        _logger = None


# -----------------------------------------------------------------------------


def __config():
    """
    Parse the config file and return the result. Internal use only.
    """
    config = ConfigParser.ConfigParser()
    success = config.read(config_path())
    if config_path() not in success:
        raise Exception('Cannot load config file ' + config_path())
    return config


def get_config():
    """
    Get a configuration object for the application, and caches it for
    future use.
    """
    global _config
    if _config is None:
        _config = __config()
    return _config


# -----------------------------------------------------------------------------


def get_connection():
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


def db_query(sql, params=None, db=None):
    """Runs a SELECT query against the database and returns the results.
    Logs and raises errors if they occur. Supply a db parameter to reuse
    a database connection if one is available, otherwise it will connect
    to the database."""
    if db is None:
        db = get_connection()

    cursor = db.cursor()
    if params is None:
        params = []

    try:
        cursor.execute(sql, params)
    except MySQLdb.Error as exception:
        log_message('Database error: {}'.format(exception), logging.CRITICAL)
        raise
    return cursor.fetchall()


def db_execute(sql, params=None, db=None, autocommit=False):
    """Runs a DML query against the database. If autocommit is false (the
    default) then there will be no call to db.commit. Supply a db parameter to
    reuse a database connection if one is available, otherwise it will connect
    to the database, and it will autocommit. Logs and raises errors if they 
    occur. Returns a count of the rows affected by the DML."""

    if db is None:
        db = get_connection()
        autocommit = True

    cursor = db.cursor()
    if params is None:
        params = []

    try:
        cursor.execute(sql, params)
    except MySQLdb.Error as exception:
        log_message('Database error: {}'.format(exception), logging.CRITICAL)
        raise

    if autocommit:
        db.commit()

    return cursor.rowcount


# -----------------------------------------------------------------------------


def __request_logger(log_type='server_log'):
    """Get a logging object. Internal use only."""
    config = get_config()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_filehandle = logging.FileHandler(
        config.get('Paths', log_type))
    log_filehandle.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_filehandle.setFormatter(log_formatter)
    logger.handlers = []
    logger.addHandler(log_filehandle)
    return logger


# @TODO use a separate error logger.
def get_logger(log_type='server_log'):
    """Get a logging object, and cache it for future use."""
    global _logger
    if _logger is None:
        _logger = {}
    if log_type not in _logger:
        _logger[log_type] = __request_logger(log_type)
    return _logger[log_type]


def log_message(message, level=logging.INFO, log_type='server_log'):
    """Log a message, with optional logging level."""
    get_logger(log_type).log(level, message)


# -----------------------------------------------------------------------------


def check_access(uuid):
    """Check access to the PLN for a journal UUID.

* If the uuid is in whitelist.txt, then the pln is accepting.
* If the uuid is in blacklist.txt, then the pln is not accepting.
* The pln is accepting if the config file says so.

 The whitelist and blacklist files are not required to exist. Lines in
 those files which start with a semicolon or are blank are ignored.
"""
    config = get_config()
    # whitelist.txt and blacklist.txt contain journal UUIDs to allow or block,
    # respectively, one UUID per line. If the files don't exist, we define
    # sensible default values for the lists.

    # Get the SWORD-server level value of accepting_deposits. If this is set to
    # 'No', don't bother checking the white or black lists.
    whitelist_path = config.get('Deposits', 'pln_accept_deposits_whitelist')
    if os.path.exists(whitelist_path):
        whitelist = [
            w.strip() for w in tuple(open(whitelist_path))
            if not w.startswith(';') and w != '\n'
        ]
    else:
        whitelist = []
    if uuid in whitelist:
        return 'Yes'

    blacklist_path = config.get('Deposits', 'pln_accept_deposits_blacklist')
    if os.path.exists(blacklist_path):
        blacklist = [
            w.strip() for w in tuple(open(blacklist_path))
            if not w.startswith(';') and w != '\n'
        ]
    else:
        blacklist = []
    if uuid in blacklist:
        return 'No'

    accepting = config.get('Deposits', 'pln_accept_deposits')
    return accepting

# -----------------------------------------------------------------------------


def timestamp_utc(dt):
    """Convert a mysql timestamp field to a UTC datetime."""
    config = get_config()
    zone = config.get('General', 'timezone')
    if zone is None:
        raise Exception('No timezone configured.')
    tz = pytz.timezone(zone)
    local_dt = tz.localize(dt)
    utc = pytz.timezone('UTC')
    return local_dt.astimezone(utc)


# -----------------------------------------------------------------------------


def get_term_languages(db=None):
    """Get a list of language codes (en-CA, en-US, etc.) from the database."""
    languages = db_query("""
            SELECT distinct(lang_code) FROM terms_of_use ORDER BY lang_code;
        """, db=db)
    if len(languages) == 0:
        m = 'Found no terms of use languages in the database.'
        log_message(m, logging.CRITICAL)
        raise PlnError(m)
    return [lang['lang_code'] for lang in languages]


def get_term_keys(db=None):
    """Get a list of keys from the database."""
    key_codes = db_query("""
            SELECT distinct(key_code) FROM terms_of_use ORDER BY key_code;
        """, db=db)
    if len(key_codes) == 0:
        m = 'Found no terms of use keys in the database.'
        log_message(m, logging.CRITICAL)
        raise PlnError(m)
    return [code['key_code'] for code in key_codes]


def get_term_details(term_id, db=None):
    """Fetch the details for a single term based on its numeric id."""
    terms = db_query("SELECT * FROM terms_of_use WHERE id = %s",
                     [term_id],
                     db=db)
    if len(terms) == 1:
        terms[0]['created'] = timestamp_utc(terms[0]['created'])
        return terms[0]
    return None


def get_term(key_code, lang_code='en-us', db=None):
    """Get current instance of a term, based on a key. key_code is a string.
    Returns one a single term if there is one or None."""
    terms = db_query("""
        SELECT * FROM terms_of_use WHERE lang_code = %s AND key_code = %s
        ORDER BY id DESC
        LIMIT 1
        """, [lang_code.lower(), key_code], db=db)
    if len(terms) == 1:
        terms[0]['created'] = timestamp_utc(terms[0]['created'])
        return terms[0]
    return None


def get_all_terms(language='en-us', db=None):
    """Get all of the terms from the database based on the available term
    keys. If there are terms which are not available in the language, then the
    en-US term will be included and a warning message will be logged. The
    result is sorted by term weights."""
    key_codes = get_term_keys(db=db)
    terms = []
    for key_code in key_codes:
        term = get_term(key_code, language, db=db)
        if term is None:
            if language == 'en-us':
                m = 'Cannot find term ' + key_code + ' in en-US'
                log_message(m, logging.CRITICAL)
                raise PlnError(m)
            else:
                log_message(
                    'Cannot find term '
                    + key_code + ' in ' + language,
                    logging.WARN
                )
                term = get_term(key_code)
        terms.append(term)
    terms.sort(key=lambda t: int(t['weight']))
    return terms


def get_terms_key(key_code, db=None):
    """Return all of the translated terms for the key, starting with the
    most recent."""
    if isinstance(key_code, dict):
        code = key_code['key_code']
    else:
        code = key_code
    terms = db_query("""
        SELECT * FROM terms_of_use WHERE key_code = %s ORDER BY id DESC
        """, [code], db=db)
    if len(terms) > 0:
        for term in terms:
            term['created'] = timestamp_utc(term['created'])
        return terms
    return None


def edit_term(term, db=None):
    """Terms are never really 'edited' so store the new version of the term
    in the database."""
    result = db_execute("""
        INSERT INTO terms_of_use (weight, key_code, lang_code, content)
        VALUES(%s, %s, %s, %s)""",  [
        term['weight'], term['key_code'], term['lang_code'],
        term['content']
    ], db=db)
    return result == 1


def update_term(term, db=None):
    """Changing the weight of a term is the only time a new version isn't saved
    to the database. Do the update."""
    db_execute("UPDATE terms_of_use SET weight = %s WHERE id = %s", [
        term['weight'], term['id']
    ], db=db)


# -----------------------------------------------------------------------------


def get_deposit(uuid, db=None):
    """Return a deposit or None from the database."""
    result = db_query('SELECT * FROM deposits WHERE deposit_uuid=%s',
                      [uuid], db=db)
    if len(result) == 0:
        return None
    return result


def get_deposits(state, db=None):
    """
    Get the deposits that have the indicated processing state value
    and return them to the microservice for processing.
    """
    return db_query("""
        SELECT * FROM deposits
        WHERE processing_state = %s AND outcome <> 'failed'
        """, [state], db=db)


def update_deposit(deposit_uuid, state, result, db=None):
    """
    Update a deposit in the database. Does not do a commit or rollback. The
    caller must decide to commit or rollback the transaction.
    """
    db_execute("""
        UPDATE deposits SET
        processing_state = %s, outcome = %s
        WHERE deposit_uuid = %s""",
               [state, result, deposit_uuid], db=db)


def record_deposit(deposit, receipt, db=None):
    """Successfully sent deposit to lockssomatic. Record the receipt. Does not
    do a commit or rollback. The caller must decide to commit or rollback
    the transaction."""
    db_execute("""
        UPDATE deposits SET
        deposit_receipt = %s,
        deposited_lom = NOW()
        WHERE deposit_uuid = %s""",
               [receipt, deposit['deposit_uuid']], db=db)


def insert_deposit(deposit_uuid, file_uuid, journal_id, deposit_action,
                   deposit_volume, deposit_issue, deposit_pubdate,
                   deposit_sha1, deposit_url, deposit_size,
                   processing_state, outcome, db=None):
    """
    Insert a deposit record to the database. Does not do a rollback() on
    failure or a commit() on success - that is the repsonsibility of the
    caller.
    """
    result = db_execute("""
        INSERT INTO deposits (deposit_uuid, file_uuid, journal_id, deposit_action,
        deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1,
        deposit_url, deposit_size, processing_state, outcome, pln_state)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        [deposit_uuid, file_uuid, journal_id, deposit_action,
                         deposit_volume, deposit_issue, deposit_pubdate,
                         deposit_sha1, deposit_url, deposit_size,
                         processing_state, outcome, "inProgress"
                         ], db=db)


# -----------------------------------------------------------------------------


def get_journal_deposits(journal_id, db=None):
    """
    Get the deposits that have the indicated processing state value
    and return them to the microservice for processing.
    """
    return db_query("""
        SELECT * FROM deposits WHERE journal_id = %s
        ORDER BY date_deposited
        """, [journal_id], db=db)


def get_journal(uuid, db=None):
    """Get a journal from the database. Returns None or 1 journal."""
    journals = db_query("SELECT * FROM journals WHERE journal_uuid = %s",
                        [uuid], db=db)
    if len(journals) == 0:
        return None
    if len(journals) == 1:
        return journals[0]
    # uuid is a unique key - there can never be more than one.


def get_journal_by_id(journal_id, db=None):
    """Get a journal from the database. Returns None or 1 journal."""
    journals = db_query("SELECT * FROM journals WHERE journal_id = %s",
                        [journal_id], db=db)
    if len(journals) == 0:
        return None
    if len(journals) == 1:
        return journals[0]
    # uuid is a unique key - there can never be more than one.


def update_journal(journal, db=None):
    db_execute("""
    UPDATE journals SET contact_date=%s, notified_date=%s, title=%s, issn=%s,
        journal_url=%s, journal_status=%s, contact_email=%s, publisher_name=%s,
        publisher_url=%s
    WHERE journal_uuid=%s
    """, [journal['contact_date'], journal['notified_date'], journal['title'],
          journal['issn'], journal['journal_url'], journal['journal_status'],
          journal['contact_email'], journal['publisher_name'],
          journal['publisher_url'], journal['journal_uuid']], db=db)


def insert_journal(journal_uuid, title, issn, journal_url, contact_email,
                   publisher_name, publisher_url, db=None):
    """
    Insert a journal record to the database. Does not do a rollback() on
    failure or a commit() on success - that is the repsonsibility of the
    caller.
    """
    db_execute("""
        INSERT INTO journals (journal_uuid, title, issn, journal_url,
        contact_email, publisher_name, publisher_url)
        VALUES(%s, %s, %s, %s, %s, %s, %s)""",
               [journal_uuid, title, issn, journal_url, contact_email,
                publisher_name, publisher_url], db=db)
    if db is not None:
        return db.insert_id()


def contacted_journal(journal_uuid, db=None):
    db_execute(
        '''UPDATE journals SET
            contact_date=now(), journal_status='healthy'
           WHERE journal_uuid=%s''',
        [journal_uuid],
        db=db
    )


def get_journals(db=None):
    """Get all distinct journals from the database, sorted by title"""
    return db_query('''select * from journals order by title''', db=db)


def get_journal_xml(uuid, db=None):
    """
    Query information about the journal that produced this deposit and wrap it
    in XML to include in the Bag.
    """
    journal = get_journal(uuid, db=db)
    if journal is None:
        return None

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


def log_microservice(service, deposit_id, start_time, end_time, result,
                     error, db=None):
    """Log the service action ot the database."""
    db_execute("""
        INSERT INTO microservices (microservice, deposit_id, started_on,
        finished_on, outcome, error) VALUES(%s, %s, %s, %s, %s, %s)""",
               [service, deposit_id, start_time, end_time, result, error], db)


# -----------------------------------------------------------------------------
# Utility methods.


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


# @TODO is this ever used?
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


def input_path(in_dir, dirs=[], filename=''):
    """Calculate an input directory based on the config file and
    any additional information.

    pkppln.input_path('processing_root', ['a', 'b'], 'foo.txt')
    """
    config = get_config()
    processing_root = config.get('Paths', 'processing_root')
    tmp_path = os.sep.join(dirs)
    path = os.path.join(processing_root, in_dir, tmp_path, filename)
    return path


def microservice_directory(state, uuid=None):
    """Find or create the directory for the microservice to work."""
    config = get_config()
    if uuid is None:
        uuid = ''
    try:
        processing_root = config.get('Paths', 'processing_root')
        path = os.path.join(processing_root, state, uuid)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    except Exception as exception:
        logging.exception(exception)
        raise exception

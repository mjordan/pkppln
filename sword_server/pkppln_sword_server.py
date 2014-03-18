"""
Simple SWORD server for the PKP Private LOCKSS Network staging server.
"""

import ConfigParser
import xml.etree.ElementTree as et
import MySQLdb as mdb
from datetime import datetime
from bottle import run, request, template, get, post, put, HTTPResponse

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

sword_server_base_url = config.get('URLs', 'sword_server_base_url')

db_host = config.get('Database', 'db_host')
db_name = config.get('Database', 'db_name')
db_user = config.get('Database', 'db_user')
db_password = config.get('Database', 'db_password')

namespaces = {'entry': 'http://www.w3.org/2005/Atom',
    'lom': 'http://lockssomatic.info/SWORD2',
    'dcterms': 'http://purl.org/dc/terms/'}
    
@get('/api/sword/2.0/sd-iri')
def service_document():
    obh = request.get_header('On-Behalf-Of')
    return template('service_document', on_behalf_of=obh, journal="Mark's test journal",
        sword_server_base_url=sword_server_base_url)

@post('/api/sword/2.0/col-iri/<on_behalf_of>')
def create_deposit(on_behalf_of):
    tree = et.parse(request.body)
    root = tree.getroot()
    title = root.find('entry:title', namespaces=namespaces)
    id = root.find('entry:id', namespaces=namespaces)
    deposit_uuid = id.text.replace('urn:uuid:', '')
    # We generate our own timestamp for inserting into the database.
    updated = root.find('entry:updated', namespaces=namespaces)
    contents = root.findall('lom:content', namespaces=namespaces)
    for content in contents:
        size = content.get('size')
        checksum_type = content.get('checksumType')
        checksum_value = content.get('checksumValue')
        
        insert_success = insert_deposit('add', deposit_uuid, on_behalf_of,
            checksum_value, content.text, size)
        
    if insert_success:
        return template('deposit_receipt', on_behalf_of=on_behalf_of, deposit_uuid=deposit_uuid,
            journal=title.text, sword_server_base_url=sword_server_base_url)
    else:
        # @todo: What do we do on failure?
        pass


    
@get('/api/sword/2.0/cont-iri/<on_behalf_of>/<deposit_uuid>/state')
def sword_statement(on_behalf_of, deposit_uuid):
    """
    SWORD state terms applicable to a PKP PLN deposit:
        failed: the deposit failed
        notinlom: deposit not yet in LOCKSS-O-Matic
        notharvested: deposit is is LOCKSS-O-Matic but not yet harvested by the PKP PLN
        harvestednoagreement: deposit has been harvested into the PKP PLN but the boxes
            are not reporting 100% Agreement.
            
        @todo: Develop logic to determine the above states. We will need to issue Statement
            request to LOM for notharvested and harvestednoagreement.
    """
    states = {
        'failed': 'Deposit failed',
        'notinlom': 'Deposit successful but not yet registered with the PKP PLN',
        'notharvested': 'Deposit registered with the PKP PLN but not fully harvested yet',
        'harvestednoagreement': 'Deposit harvested into PKP PLN but polling still in progress'
    }
    con = mdb.connect(db_host, db_user, db_password, db_name)
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT issue_url FROM archived_issues WHERE journal_uuid = %s", deposit_uuid)
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    
    if cur.rowcount:
        files = []
        for row in cur:
            files.append(str(row[0]))
            # For now just use 'notinlom'.
        return template('sword_statement', files=files, state_term='notinlom', 
            state_description=states['notinlom'])
    else:
        return bottle.HTTPResponse(status=404)


@put('/api/sword/2.0/cont-iri/<on_behalf_of>/<deposit_uuid>/edit')
def edit_deposit(on_behalf_of, deposit_uuid):
    """
    OJS issues a deposit edit request to the CONT-IRI/Edit-IRI using a subset of
    the Atom document that originally created the deposit.
    """
    tree = et.parse(request.body)
    root = tree.getroot()
    id = root.find('entry:id', namespaces=namespaces)
    deposit_uuid = id.text.replace('urn:uuid:', '')
    updated = root.find('entry:updated', namespaces=namespaces)
    # We generate our own timestamp for inserting into the database.
    contents = root.findall('lom:content', namespaces=namespaces)
    for content in contents:
        logging.info(content.text)
        size = content.get('size')
        checksum_type = content.get('checksumType')
        checksum_value = content.get('checksumValue')
        
        insert_success = insert_deposit('edit', deposit_uuid, on_behalf_of, checksum_value, content.text, size)
        
    if insert_success:
        return HTTPResponse(status=200)
    else:
        # @todo: What do we do on failure?
        pass

def insert_deposit(action, deposit_uuid, on_behalf_of, checksum_value, url, size):
    con = mdb.connect(db_host, db_user, db_password, db_name)
    try:
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO archived_issues " +
                "(action, date_deposited, deposit_uuid, journal_uuid, sha1_value, issue_url, size, harvested, deposited_lom) " +
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (action, datetime.now(), deposit_uuid,
                on_behalf_of, checksum_value, url, size, None, None))
        return True
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        return False
    
# Run Bottle's built-in development web server.
run(host='localhost', port=9999)

"""
Simple SWORD server for the PKP Private LOCKSS Network staging server.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import sys
import MySQLdb
import MySQLdb.cursors
import xml.etree.ElementTree as et
from datetime import datetime
import ConfigParser
from bottle import run, request, template, get, post, put, HTTPResponse

# sys.path.append("/opt/pkppln")
sys.path.append("/home/mark/Documents/apache_thinkpad/pkppln")

import staging_server_common

# For debugging during development.
import logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format=logging.BASIC_FORMAT)

config = ConfigParser.ConfigParser()
# config.read('/opt/pkppln/config_dev.cfg')
config.read('../config_dev.cfg')

# Define variables.
sword_server_base_url = config.get('URLs', 'sword_server_base_url')
namespaces = {'entry': 'http://www.w3.org/2005/Atom',
    'pkp': 'http://pkp.sfu.ca/SWORD',
    'dcterms': 'http://purl.org/dc/terms/'}

@get('/api/sword/2.0/sd-iri')
def service_document():
    """
    Routing for retrieving the Service Document.
    """

    obh = request.headers.get('On-Behalf-Of')
    language = request.headers.get('Accept-Language', 'en-US')

    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("SELECT * FROM terms_of_use WHERE language = %s", language)
    except MySQLdb.Error, e:
        logging.exception(e)
        sys.exit(1)
    
    if cur.rowcount:
        terms_of_use = []
        for row in cur:
            terms_of_use.append(row)
        return template('service_document', on_behalf_of=obh, terms=terms_of_use,
            sword_server_base_url=sword_server_base_url)
    else:
        return HTTPResponse(status=404)

@post('/api/sword/2.0/col-iri/<on_behalf_of>')
def create_deposit(on_behalf_of):
    """
    Routing for creating a Deposit. On-Behalf-Of is
    the journal UUID.
    """
    tree = et.parse(request.body)
    root = tree.getroot()
    title = root.find('entry:title', namespaces=namespaces)
    issn = root.find('pkp:issn', namespaces=namespaces)
    email = root.find('entry:email', namespaces=namespaces)
    id = root.find('entry:id', namespaces=namespaces)
    deposit_uuid = id.text.replace('urn:uuid:', '')
    deposit_details = root.find('pkp:details', namespaces=namespaces)
    # We generate our own timestamp for inserting into the database.
    # updated = root.find('entry:updated', namespaces=namespaces)
    contents = root.findall('pkp:content', namespaces=namespaces)
    for content in contents:
        size = content.get('size')
        checksum_type = content.get('checksumType')
        checksum_value = content.get('checksumValue')
        deposits_insert_success = staging_server_common.insert_deposit('edit', deposit_uuid, deposit_details, on_behalf_of,
            checksum_value, content.text, size, 'depositedByJournal', 'success')
    if deposits_insert_success:
        journals_insert_success = staging_server_common.insert_journal(on_behalf_of, title.text, issn.text, email.text, deposit_uuid)
        return template('deposit_receipt', on_behalf_of=on_behalf_of, deposit_uuid=deposit_uuid,
            journal_title=title.text, sword_server_base_url=sword_server_base_url)
    else:
        # What error code do we use if the deposit failed? Also, if the database insert failed,
        # how do we record this in the database?
        return HTTPResponse(status=201)

@get('/api/sword/2.0/cont-iri/<on_behalf_of>/<deposit_uuid>/state')
def sword_statement(on_behalf_of, deposit_uuid):
    """
    Routing for retrieving a SWORD Statement.
    
    SWORD state terms applicable to a deposit to the PKP PLN (taken from the
        LOCKSS-O-Matic SWORD API state terms but with modified descriptions):
        failed: The deposit to the PKP PLN staging server (or LOCKSS-O-Matic) has failed.
        in_progress: The deposit to the staging server has succeeded but the deposit has not yet been registered with the PLN.
        disagreement: The PKP LOCKSS network is not in agreement on content checksums.
        agreement: The PKP LOCKSS network agrees internally on content checksums.
            
        @todo: Develop logic to determine the above states, i.e., pass through LOCKSS-O-Matic's
        state terms.
    """
    states = {
        'failed': 'The deposit to the PKP PLN staging server (or LOCKSS-O-Matic) has failed.',
        'in_progress': 'The deposit to the staging server has succeeded but the deposit has not yet been registered with the PLN.',
        'disagreement': 'The PKP LOCKSS network is not in agreement on content checksums.',
        'agreement': 'The PKP LOCKSS network agrees internally on content checksums.'
    }
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("SELECT deposit_url FROM deposits WHERE deposit_uuid = %s", deposit_uuid)
    except MySQLdb.Error, e:
        logging.exception(e)
        sys.exit(1)
    
    if cur.rowcount:
        files = []
        for row in cur:
            files.append(str(row[0]))
            # Until we address the previous @todo, use 'agreement'.
        return template('sword_statement', files=files, state_term='agreement', 
            state_description=states['agreement'])
    else:
        return HTTPResponse(status=404)

@put('/api/sword/2.0/cont-iri/<on_behalf_of>/<deposit_uuid>/edit')
def edit_deposit(on_behalf_of, deposit_uuid):
    """
    Routing for updating metadata about a Deposit.
    
    OJS issues a deposit edit request to the CONT-IRI/Edit-IRI using a subset of
    the Atom document that originally created the deposit.
    """
    tree = et.parse(request.body)
    root = tree.getroot()
    email = root.find('entry:email', namespaces=namespaces)
    id = root.find('entry:id', namespaces=namespaces)
    deposit_uuid = id.text.replace('urn:uuid:', '')
    # We generate our own timestamp for inserting into the database.
    # updated = root.find('entry:updated', namespaces=namespaces)    
    contents = root.findall('pkp:content', namespaces=namespaces)
    for content in contents:
        size = content.get('size')
        checksum_type = content.get('checksumType')
        checksum_value = content.get('checksumValue')
        insert_success = staging_server_common.insert_deposit('edit', email.text, deposit_uuid, on_behalf_of, checksum_value, content.text, size, 'depositedByJournal', 'success')      
    if insert_success:
        return HTTPResponse(status=201)
    else:
        # What error code do we use if the deposit failed? Also, if the database insert failed,
        # how do we record this in the database?
        return HTTPResponse(status=201)

# Run Bottle's built-in development web server.
run(host=config.get('URLs', 'sword_server_host'), port=config.get('URLs', 'sword_server_port'))

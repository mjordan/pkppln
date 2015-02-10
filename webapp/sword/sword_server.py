"""
Simple SWORD server for the PKP Private LOCKSS Network staging server.

Copyright (c) 2014-2015 Simon Fraser University Library
Copyright (c) 2014-2015 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import sys
from os.path import dirname
import xml.etree.ElementTree as et
import MySQLdb
from _elementtree import XMLParser
import logging
import bottle
from bottle import request, template, get, post, put, HTTPResponse, response

import pkppln
from pkppln import namespaces

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')


@get('/api/sword/2.0/sd-iri')
def service_document():
    """
    Routing for retrieving the Service Document.
    """
    config = pkppln.get_config()
    obh = request.headers.get('On-Behalf-Of')
    journal_url = request.headers.get('Journal-URL')
    language = request.headers.get('Accept-Language', 'en-US')

    if obh is None:
        return HTTPResponse(status=400, body='Missing On-Behalf-Of header')

    if journal_url is None:
        return HTTPResponse(status=400, body='Missing Journal-URL header')

    pkppln.log_message(
        '\t'.join([request.get('REMOTE_ADDR'), 'sd', obh, journal_url]))

    # Get the 'accepting deposits' value.
    accepting = pkppln.check_access(obh)
    terms = pkppln.get_all_terms(language)

    if len(terms) > 0:
        return template(
            'service_document',
            accepting=accepting,
            on_behalf_of=obh,
            terms=terms,
            sword_server_base_url=config.get('URLs', 'sword_server_base_url'))
    else:
        return HTTPResponse(status=404)


# @put('/api/sword/2.0/cont-iri/<on_behalf_of>/<deposit_uuid>/edit')


def insert_content(deposit_action, deposit_uuid, journal_uuid, content):
    deposit_sha1 = content.get('checksumValue')
    deposit_volume = content.get('volume')
    deposit_issue = content.get('issue')
    deposit_pubdate = content.get('pubdate')
    deposit_size = content.get('size')
    deposit_url = content.text

    return pkppln.insert_deposit(
        deposit_uuid, journal_uuid, deposit_action,
        deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1,
        deposit_url, deposit_size, 'depositedByJournal', 'success')


@post('/api/sword/2.0/col-iri/<journal_uuid>')
def create_deposit(journal_uuid):
    """
    Routing for creating a Deposit. On-Behalf-Of is
    the journal UUID.
    """
    config = pkppln.get_config()
    if len(journal_uuid) == 0:
        return HTTPResponse(status=400)

    root = et.fromstring(
        request.body.getvalue(),
        parser=XMLParser(encoding='UTF-8')
    )

    pkppln.log_message(request.body.getvalue())

    title = root.find('entry:title', namespaces).text
    issn = root.find('pkp:issn', namespaces).text
    journal_url = root.find('pkp:journal_url', namespaces).text

    node = root.find('pkp:publisherName', namespaces)
    if node is not None and node.text is not None:
        publisher_name = node.text
    else:
        publisher_name = '(unknown)'

    node = root.find('pkp:publisherUrl', namespaces)
    if node is not None and node.text is not None:
        publisher_url = node.text
    else:
        publisher_url = ''

    email = root.find('entry:email', namespaces).text
    urn_id = root.find('entry:id', namespaces).text
    deposit_uuid = urn_id.replace('urn:uuid:', '')

    pkppln.log_message('\t'.join([request.get('REMOTE_ADDR'), 'create',
                                  journal_uuid, deposit_uuid]))

    journal = pkppln.get_journal(journal_uuid)
    if journal is None:
        result = pkppln.insert_journal(journal_uuid, title, issn, journal_url,
                                       email, publisher_name, publisher_url)
        if result:
            pkppln.db_commit()

    # We generate our own timestamp for inserting into the database.
    # updated = root.find('entry:updated', namespaces=namespaces)
    contents = root.findall('pkp:content', namespaces)

    for content in contents:
        if insert_content('add', deposit_uuid, journal_uuid, content) is False:
            return HTTPResponse(status=501)
    pkppln.db_commit()

    # @todo how do i set the location?
    response.status = 201
    response.set_header('Location', '/'.join((
        '', 'api', 'sword', '2.0', 'cont-iri', journal_uuid, deposit_uuid, 'edit')
    ))
    return template('deposit_receipt', journal_uuid=journal_uuid,
                    deposit_uuid=deposit_uuid, journal_title=title,
                    sword_server_base_url=config.get(
                        'URLs', 'sword_server_base_url')
                    )


@get('/api/sword/2.0/cont-iri/<journal_uuid>/<deposit_uuid>/state')
def sword_statement(journal_uuid, deposit_uuid):
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

    if len(journal_uuid) == 0 or len(deposit_uuid) == 0:
        return HTTPResponse(status=400)

    pkppln.log_message(
        '\t'.join([request.get('REMOTE_ADDR'), 'state', journal_uuid, deposit_uuid]))

    states = {
        'failed': 'The deposit to the PKP PLN staging server (or LOCKSS-O-Matic) has failed.',
        'in_progress': 'The deposit to the staging server has succeeded but the deposit has not yet been registered with the PLN.',
        'disagreement': 'The PKP LOCKSS network is not in agreement on content checksums.',
        'agreement': 'The PKP LOCKSS network agrees internally on content checksums.'
    }
    try:
        cursor = pkppln.get_connection().cursor()
        cursor.execute(
            """
            SELECT * FROM deposits 
            WHERE deposit_uuid = %s AND journal_uuid=%s""",
            [deposit_uuid, journal_uuid]
        )
    except MySQLdb.Error as error:
        pkppln.log_message(error.message, level=logging.CRITICAL)
        sys.exit(1)

    deposits = list(cursor.fetchall())
    if len(deposits) > 0:
        # Until we address the previous @todo, use 'agreement'.
        return template('sword_statement', deposit=deposits[0], states=states)
    else:
        return HTTPResponse(status=404)


@put('/api/sword/2.0/cont-iri/<journal_uuid>/<deposit_uuid_param>/edit')
def edit_deposit(journal_uuid, deposit_uuid_param):
    """
    Routing for creating a Deposit. On-Behalf-Of is
    the journal UUID.
    """
    config = pkppln.get_config()
    if len(journal_uuid) == 0:
        return HTTPResponse(status=400)

    root = et.fromstring(
        request.body.getvalue(),
        parser=XMLParser(encoding='UTF-8')
    )

    title = root.find('entry:title', namespaces).text
    issn = root.find('pkp:issn', namespaces).text
    journal_url = root.find('pkp:journal_url', namespaces).text
    email = root.find('entry:email', namespaces).text
    publisher_name = root.find('pkp:publisherName', namespaces).text
    publisher_url = root.find('pkp:publisherUrl', namespaces).text
    urn_id = root.find('entry:id', namespaces).text
    deposit_uuid = urn_id.replace('urn:uuid:', '')

    if deposit_uuid != deposit_uuid_param:
        return HTTPResponse(status=400)

    pkppln.log_message('\t'.join([request.get('REMOTE_ADDR'), 'edit',
                                  journal_uuid, deposit_uuid]))

    # We generate our own timestamp for inserting into the database.
    # updated = root.find('entry:updated', namespaces=namespaces)
    contents = root.findall('pkp:content', namespaces)

    # SHOULD BE A START TRANSACTION HERE.
    mysql = pkppln.get_connection()
    for content in contents:
        if insert_content('edit', deposit_uuid, journal_uuid, content) is False:
            mysql.rollback()
            return HTTPResponse(status=501)

    if pkppln.insert_journal(journal_uuid, title, issn, journal_url, email,
                             deposit_uuid, publisher_name, publisher_url) is False:
        mysql.rollback()
        return HTTPResponse(status=501)

    mysql.commit()

    response.status = 201
    response.set_header('Location', '/'.join((
        '', 'api', 'sword', '2.0', 'cont-iri', journal_uuid, deposit_uuid, 'edit')
    ))
    return template('deposit_receipt', journal_uuid=journal_uuid,
                    deposit_uuid=deposit_uuid, journal_title=title,
                    sword_server_base_url=config.get(
                        'URLs', 'sword_server_base_url')
                    )

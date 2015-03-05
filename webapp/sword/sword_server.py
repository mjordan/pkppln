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
import uuid

import pkppln
from pkppln import namespaces
from uuid import uuid4

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')


from webapp.webapp import WebApp


class SwordServer(WebApp):

    def __init__(self, name):
        WebApp.__init__(self, "SwordApp")
        self.route('/sd-iri', method='GET',
                   callback=self.service_document)
        self.route('/col-iri/<journal_uuid>', method='POST',
                   callback=self.create_deposit)
        self.route('/cont-iri/<journal_uuid>/<deposit_uuid>/state',
                   method='GET', callback=self.sword_statement)
        self.route('/cont-iri/<journal_uuid>/<deposit_uuid_param>/edit',
                   method='PUT', callback=self.edit_deposit)

    def service_document(self):
        """
        Routing for retrieving the Service Document.
        """
        config = pkppln.get_config()
        handle = pkppln.get_connection()
        obh = request.headers.get('On-Behalf-Of')
        journal_url = request.headers.get('Journal-URL')
        # language = request.headers.get('Accept-Language', 'en-US')
        # @TODO language needs to be processed a bit:
        # en-CA,en;q=0.8,en-GB;q=0.6,en-US;q=0.4
        language = 'en-US'
        if obh is None:
            obh = request.query.get('obh')
        if journal_url is None:
            journal_url = request.query.get('journal_url')

        if obh is None:
            return HTTPResponse(status=400, body='Missing On-Behalf-Of header')

        if journal_url is None:
            return HTTPResponse(status=400, body='Missing Journal-URL header')

        pkppln.contacted_journal(obh, db=handle)
        handle.commit()

        # Get the 'accepting deposits' value.
        accepting = pkppln.check_access(obh)
        terms = pkppln.get_all_terms(language, db=handle)

        if len(terms) > 0:
            response.content_type = 'text/xml; charset=UTF-8'
            return template(
                'service_document',
                accepting=accepting,
                on_behalf_of=obh,
                terms=terms,
                sword_server_base_url=config.get('URLs', 'sword_server_base_url'))
        else:
            return HTTPResponse(status=404)

    def insert_content(self, deposit_action, deposit_uuid, file_uuid,
                       journal_id, content, db=None):
        deposit_sha1 = content.get('checksumValue')
        deposit_volume = content.get('volume')
        deposit_issue = content.get('issue')
        deposit_pubdate = content.get('pubdate')
        deposit_size = content.get('size')
        deposit_url = content.text

        return pkppln.insert_deposit(
            deposit_uuid, file_uuid, journal_id, deposit_action,
            deposit_volume, deposit_issue, deposit_pubdate, deposit_sha1,
            deposit_url, deposit_size, 'depositedByJournal', 'success', db)

    def create_deposit(self, journal_uuid):
        """
        Routing for creating a Deposit. On-Behalf-Of is
        the journal UUID.
        """
        config = pkppln.get_config()
        handle = pkppln.get_connection()
        if len(journal_uuid) == 0:
            return HTTPResponse(status=400)

        root = et.fromstring(
            request.body.getvalue(),
            parser=XMLParser(encoding='UTF-8')
        )

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
            publisher_url = '(unknown)'

        email = root.find('entry:email', namespaces).text
        urn_id = root.find('entry:id', namespaces).text
        deposit_uuid = urn_id.replace('urn:uuid:', '')

        journal = pkppln.get_journal(journal_uuid, db=handle)
        if journal is None:
            journal = {}
            try:
                journal['id'] = pkppln.insert_journal(
                    journal_uuid, title, issn, journal_url,
                    email, publisher_name, publisher_url, db=handle
                )
            except:
                handle.rollback()
                raise
            # don't commit yet.

        # We generate our own timestamp for inserting into the database.
        # updated = root.find('entry:updated', namespaces=namespaces)
        contents = root.findall('pkp:content', namespaces)

        for content in contents:
            file_uuid = uuid.uuid4()
            try:
                self.insert_content('add', deposit_uuid, file_uuid,
                                    journal['id'], content, db=handle)
            except:
                handle.rollback()
                raise

        pkppln.contacted_journal(journal_uuid, db=handle)
        handle.commit()

        response.status = 201
        response.set_header('Location', '/'.join((
            '', 'api', 'sword', '2.0', 'cont-iri', journal_uuid,
            deposit_uuid, 'edit')
        ))
        response.content_type = 'text/xml; charset=UTF-8'
        return template('deposit_receipt', journal_uuid=journal_uuid,
                        deposit_uuid=deposit_uuid, journal_title=title,
                        sword_server_base_url=config.get(
                            'URLs', 'sword_server_base_url')
                        )

    def sword_statement(self, journal_uuid, deposit_uuid):
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

        states = {
            'failed': 'The deposit to the PKP PLN staging server (or LOCKSS-O-Matic) has failed.',
            'inProgress': 'The deposit to the staging server has succeeded but the deposit has not yet been registered with the PLN.',
            'disagreement': 'The PKP LOCKSS network is not in agreement on content checksums.',
            'agreement': 'The PKP LOCKSS network agrees internally on content checksums.',
            'unknown': 'The deposit is in an unknown state.'
        }
        handle = pkppln.get_connection()

        deposit = pkppln.get_deposit(deposit_uuid, db=handle)
        if deposit is None:
            return HTTPResponse(status=404)
        journal = pkppln.get_journal(journal_uuid, db=handle)

        if deposit['journal_id'] != journal['id']:
            return HTTPResponse(status=400)

        pkppln.contacted_journal(journal_uuid, db=handle)
        return template('sword_statement', deposit=deposit, states=states)

    def edit_deposit(self, journal_uuid, deposit_uuid_param):
        """
        Routing for creating a Deposit. On-Behalf-Of is
        the journal UUID.
        """
        config = pkppln.get_config()
        handle = pkppln.get_connection()
        if len(journal_uuid) == 0:
            return HTTPResponse(status=400)

        root = et.fromstring(
            request.body.getvalue(),
            parser=XMLParser(encoding='UTF-8')
        )

        title = root.find('entry:title', namespaces).text
        urn_id = root.find('entry:id', namespaces).text
        deposit_uuid = urn_id.replace('urn:uuid:', '')

        if deposit_uuid != deposit_uuid_param:
            return HTTPResponse(status=400)

        journal = pkppln.get_journal(journal_uuid, db=handle)
        if journal is None:
            # Don't try to create a new journal - it must already exist.
            return HTTPResponse(status=400)

        contents = root.findall('pkp:content', namespaces)
        for content in contents:
            file_uuid = uuid.uuid4()
            try:
                self.insert_content('edit', deposit_uuid, file_uuid,
                                    journal['id'], content, db=handle)
            except:
                handle.rollback()
                raise

        pkppln.contacted_journal(journal_uuid, db=handle)
        handle.commit()

        response.status = 201
        response.set_header('Location', '/'.join((
            '', 'api', 'sword', '2.0', 'cont-iri', journal_uuid,
            deposit_uuid, 'edit')
        ))
        response.content_type = 'text/xml'
        return template('deposit_receipt', journal_uuid=journal_uuid,
                        deposit_uuid=deposit_uuid, journal_title=title,
                        sword_server_base_url=config.get(
                            'URLs', 'sword_server_base_url')
                        )

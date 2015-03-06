"""
Simple CRUD tool for PKP PLN terms of use.

Copyright (c) 2014-2015 Simon Fraser University Library
Copyright (c) 2014-2015 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

# @todo Add filters to routes as per http://bottlepy.org/docs/dev/routing.html

from os.path import dirname
from bottle import Bottle, request, template
import bottle
import pkppln
import math

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')

from webapp.webapp import WebApp

PER_PAGE = 25


class JournalsApp(WebApp):

    def __init__(self, name):
        WebApp.__init__(self, "JournalsApp")
        self.route('/', method='GET', callback=self.journal_list)
        self.route('/detail/:uuid', method='GET', callback=self.journal_detail)
        self.route('/health/:uuid', method='GET', callback=self.journal_health)
        self.route(
            '/health/:uuid', method='POST', callback=self.journal_health_update)
        self.route(
            '/deposits/:uuid', method='GET', callback=self.journal_deposits)

    def journal_list(self):
        handle = pkppln.get_connection()
        page = int(request.GET.get('p', '1').strip())
        if page <= 0:
            page = 1
        offset = (page - 1) * PER_PAGE
        journals = pkppln.db_query(
            'SELECT * FROM journals ORDER BY title LIMIT %s OFFSET %s',
            [PER_PAGE, offset],
            db=handle
        )
        total_result = pkppln.db_query(
            'SELECT count(*) c FROM journals',
            db=handle
        )
        total = int(total_result[0]['c'])
        pages = int(math.ceil(float(total) / PER_PAGE))
        return template('journals_list', page=page, total=total, pages=pages,
                        journals=journals)

    def journal_detail(self, uuid):
        handle = pkppln.get_connection()
        journal = pkppln.get_journal(uuid, db=handle)
        total_result = pkppln.db_query(
            'SELECT count(*) c FROM deposits WHERE journal_id=%s',
            [journal['id']],
            db=handle
        )
        total = int(total_result[0]['c'])
        return template('journal_detail', journal=journal, deposits=total)

    def journal_deposits(self, uuid):
        handle = pkppln.get_connection()
        journal = pkppln.get_journal(uuid, db=handle)
        page = int(request.GET.get('p', '1').strip())
        if page <= 0:
            page = 1
        offset = (page - 1) * PER_PAGE
        deposits = pkppln.db_query(
            '''SELECT * FROM deposits WHERE journal_id = %s
            ORDER BY date_deposited DESC LIMIT %s OFFSET %s''',
            [journal['id'], PER_PAGE, offset],
            db=handle)
        total_result = pkppln.db_query(
            'SELECT count(*) c FROM deposits WHERE journal_id=%s',
            [journal['id']],
            db=handle
        )
        total = int(total_result[0]['c'])
        pages = int(math.ceil(float(total) / PER_PAGE))
        return template('journal_deposits', page=page, total=total, pages=pages,
                        journal=journal, deposits=deposits)

    def journal_health(self, uuid):
        pass

    def journal_health_update(self, uuid):
        pass

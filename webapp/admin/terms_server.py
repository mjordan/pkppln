"""
Simple CRUD tool for PKP PLN terms of use.

Copyright (c) 2014-2015 Simon Fraser University Library
Copyright (c) 2014-2015 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

# @todo: Add filters to routes as per http://bottlepy.org/docs/dev/routing.html.

import sys
from os.path import dirname
import re
import MySQLdb
from datetime import datetime
from bottle import request, template, get, post, route
import bottle
import pkppln
import logging

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')


def get_term_details(term_id):
    """Fetch the details for a single term."""
    try:
        cursor = pkppln.get_connection().cursor()
        cursor.execute("SELECT * FROM terms_of_use WHERE id = %s", [term_id])
        term = cursor.fetchone()
    except MySQLdb.Error as exception:
        pkppln.log_message(exception, level=logging.CRITICAL)
        sys.exit(1)
    return term


@get('/admin/terms/list_terms')
@get('/admin/terms/list')
def terms_list():
    """Show all the terms."""
    lang = request.query.lang or 'en-us'
    pkppln.log_message(
        request.get('REMOTE_ADDR') + ' - ' + 'admin/terms/list ' + lang)
    terms = pkppln.get_all_terms(lang)
    languages = pkppln.get_term_languages()

    if len(terms):
        return template('terms_list', languages=languages, terms=terms)
    else:
        return template('messages', section='no_terms',
                        message='Sorry, there are no terms of use.')


@get('/admin/terms/detail/<key_code>')
def term_detail(key_code):
    try:
        cursor = pkppln.get_connection().cursor()
        cursor.execute("""
        SELECT * FROM terms_of_use
        WHERE key_code = %s
        ORDER BY id DESC
        """, [key_code])
    except MySQLdb.Error as exception:
        pkppln.log_message(exception, level=logging.CRITICAL)
        sys.exit(1)
    terms = cursor.fetchall()
    return template('term_detail', terms=terms, key_code=key_code)


@get('/admin/terms/sort')
def terms_sort():
    """Show all the terms."""
    pkppln.log_message(request.get('REMOTE_ADDR') + '\t' + 'admin/terms/sort')
    terms = pkppln.get_all_terms()
    return template('terms_sort', terms=terms, message=None)


@post('/admin/terms/sort')
def terms_sort_save():
    pkppln.log_message(request.get('REMOTE_ADDR') + '\t' + 'admin/terms/sort')
    term_order = request.forms.get('order').split(',')
    for idx, key in enumerate(term_order):
        terms = pkppln.get_terms_key(key)
        for term in terms:
            term['weight'] = idx
            pkppln.update_term(term)
    terms = pkppln.get_all_terms()
    return template('terms_sort', terms=terms, message="Saved")


@get('/admin/terms/add_term')
def add_term(term_id=''):
    """Add a new term."""
    term = {'lang_code': 'en-US', 'key_code': '', 'content': ''}
    return template('crud_form', form_title='Create a new Term', **term)


@get('/admin/terms/edit_term/:key_code')
@get('/admin/terms/edit_term/:key_code/:lang_code')
def edit_term(key_code, lang_code='en-us'):
    """We need to keep all versions of each term of use."""
    pkppln.log_message(request.get('REMOTE_ADDR') + ' - '
                       + '/'.join(['admin/terms/edit/', key_code, lang_code]))
    form_title = 'Edit term of use'
    term = pkppln.get_term(key_code, lang_code)
    if term is None:
        return template('messages',
                        message='That term does not exist.')
    if term['lang_code'] != lang_code:
        return template('messages',
                        message='The term does not exist in that language.')
    return template('crud_form', action='edit',
                    form_title=form_title, **term)


@post('/admin/terms/save')
def save_term():
    """
    """
    term = {}
    term['lang_code'] = request.forms.get('language').strip()
    term['key_code'] = request.forms.get('key').strip()
    term['content'] = request.forms.get('text').strip()
    term['id'] = request.forms.get('id', '').strip()
    term['weight'] = request.forms.get('weight', '1').strip()

    pkppln.log_message(request.get('REMOTE_ADDR') + ' - '
                       + ' '.join(['/admin/terms/save', term['id'],
                                   term['key_code'], term['lang_code']]))
    pkppln.edit_term(term)
    return template('messages',
                    message='A new version of the term has been saved.')

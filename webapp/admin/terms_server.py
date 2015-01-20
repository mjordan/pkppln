"""
Simple CRUD tool for PKP PLN terms of use.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

# @todo: Add filters to routes as per http://bottlepy.org/docs/dev/routing.html.

import sys
from os.path import dirname
import re
import MySQLdb
from datetime import datetime
from bottle import request, template, get, post
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


@get('/admin/terms/list')
def terms_list():
    """Show all the terms."""
    pkppln.log_message(request.get('REMOTE_ADDR') + '\t' + 'admin/terms/list')

    try:
        cursor = pkppln.get_connection().cursor()
        cursor.execute("SELECT * FROM terms_of_use")
        terms = cursor.fetchall()
    except MySQLdb.Error as exception:
        pkppln.log_message(exception, level=logging.CRITICAL)
        sys.exit(1)

    if len(terms):
        return template('terms_list', terms=terms)
    else:
        return template('messages', section='no_terms',
                        message='Sorry, there are no terms of use.')


@get('/admin/terms/add_term/:term_id')
def add_term(term_id=''):
    """Add a new term."""
    # If this is a brand new term
    if term_id == 'new':
        form_title = 'Add term of use'
        term_values = {'id': None, 'language': '', 'key': '', 'text': ''}
        action = 'new'
    # If it's a clone of an existing one.
    else:
        form_title = 'Clone term of use'
        term_values = get_term_details(term_id)
        action = 'clone'
    return template('crud_form', action=action,
                    form_title=form_title, **term_values)


@get('/admin/terms/edit_term/:term_id')
def edit_term(term_id):
    """We need to keep all versions of each term of use. The
    current_version field indicates whether a term is to appear in the
    SWORD Service Document (i.e., if its value is 'Yes'). In order to
    keep all vesions, we don't perform an UPDATE SQL query, we always
    perfom INSERTs, using the using the key and language values from
    the source term row and addding new term_id, current_version,
    last_updates, and text values. The current_version value for the
    source terms row will also need to be set to 'No'.

    """
    pkppln.log_message(request.get('REMOTE_ADDR')
                       + '\t' + 'admin/terms/edit/' + term_id)
    form_title = 'Edit term of use'
    term_values = get_term_details(term_id)
    return template('crud_form', action='edit',
                    form_title=form_title, **term_values)


@get('/admin/terms/delete_term/:term_id')
def delete_term_of_use(term_id):
    """Delete one of the terms of use."""
    pkppln.log_message(request.get('REMOTE_ADDR') + '\t' + 'admin/terms/delete/' + term_id)
    try:
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute("DELETE FROM terms_of_use WHERE id = %s", [term_id])
        rows_affected = cursor.rowcount
    except MySQLdb.Error as exception:
        mysql.rollback()
        pkppln.log_message(exception, level=logging.CRITICAL)
        sys.exit(1)

    if rows_affected == 1:
        mysql.commit()
        return template('messages', section='term_deleted',
                        message='The term has been deleted.')
    else:
        mysql.rollback()
        return template('messages', section='term_not_deleted',
                        message='The term has not been deleted.')


@post('/admin/terms/insert_new_term')
def insert_new_term_of_use():
    """
    We don't update rows in this application, we only add new ones.
    """
    language = request.forms.get('language').strip()
    key = request.forms.get('key').strip()
    text = request.forms.get('text')
    action = request.forms.get('action')

    term_id = request.forms.get('id')
    pkppln.log_message(request.get('REMOTE_ADDR') + '\t' + 'admin/terms/insert/' + term_id)

    mysql = pkppln.get_connection()
    cursor = mysql.cursor()

    try:
        cursor.execute("""
        INSERT INTO terms_of_use
            (current_version, last_updated, `key`, language, text)
        VALUES(%s, %s, %s, %s, %s)""",
                       ('Yes', datetime.now(), key, language, text))
        if action == 'edit':
            cursor.execute("""
            UPDATE terms_of_use SET current_version = 'No' WHERE id = %s""",
                           [term_id])
            message = 'The term of use has been updated.'
            section = 'term_updated'
        else:
            message = 'The term of use has been added.'
            section = 'term_added'

        mysql.commit()
        return template('messages', section=section, message=message)
    except MySQLdb.Error as exception:
        mysql.rollback()
        pkppln.log_message(exception, level=logging.CRITICAL)
        sys.exit(1)

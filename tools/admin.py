"""
Simple CRUD tool for PKP PLN terms of use.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

# @todo: Add filters to routes as per http://bottlepy.org/docs/dev/routing.html.

import sys
import re
import MySQLdb
import MySQLdb.cursors
from bottle import route, run, template, debug, static_file, redirect, request
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/home/mark/Documents/apache_thinkpad/pkppln/config_dev.cfg')

def get_term_details(id):
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'),
            cursorclass=MySQLdb.cursors.DictCursor)
        cur = con.cursor()
        cur.execute("SELECT * FROM terms_of_use WHERE id = %s", id)
        term = cur.fetchone()
    except MySQLdb.Error, e:
        sys.exit(1)

    return term

@route('/list_terms')
def list_terms_of_use():
    # @todo: Allow limiting to locale and key, possibly via links in the list.
    language = 'en-US'
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("SELECT * FROM terms_of_use WHERE language = %s AND current_version = 'Yes'", language)
        result = cur.fetchall()
    except MySQLdb.Error, e:
        sys.exit(1)

    if len(result):
        rows = list(result)
        return template('list_terms_of_use', rows=rows)
    else:
        return template('messages', section='no_terms', message='Sorry, there are no terms of use.')

@route('/add_term/:id')
def add_term_of_use(id=''):
    # If it's a brand-new term of use.
    if id == 'new':
        form_title = 'Add term of use'
        term_values = {'language': '', 'key': '', 'text': ''}
    # If it's a clone of an existing one.
    else:
        form_title = 'Clone term of use'
        term_values = get_term_details(id)
    disabled = ''
    return template('crud_form', term_values=term_values, form_title=form_title, disabled=disabled)

@route('/edit_term/:id')
def edit_term_of_use(id):
    """
    We need to keep all versions of each term of use. The current_version field indicates whether
    a term is to appear in the SWORD Service Document (i.e., if its value is 'Yes'). In order to
    keep all vesions, we don't perform an UPDATE SQL query, we always perfom INSERTs, using the
    using the key and language values from the source term row and addding new id, current_version,
    last_updates, and text values. The current_version value for the source terms row will also need
    to be set to 'No'.
    """
    form_title = 'Edit term of use'
    term_values = get_term_details(id)
    disabled = 'disabled'
    return template('crud_form', term_values=term_values, form_title=form_title, disabled=disabled)

@route('/delete_term/:id')
def delete_term_of_use(id):
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("DELETE FROM terms_of_use WHERE id = %s", id)
        rows_affected=cur.rowcount
        con.commit()
    except MySQLdb.Error, e:
        sys.exit(1)

    if rows_affected == 1:
        return template('messages', section='term_deleted', message='Term deleted.')
    else:
        return template('messages', section='term_not_deleted', message='Sorry, there was a problem deleting the term of use.')

# Routes for static files - CSS, Javascript, etc.
@route('/css/<filename:path>')
def server_static(filename):
    return static_file(filename, root='/home/mark/Documents/apache_thinkpad/pkppln/tools/views/css')

@route('/js/<filename:path>')
def server_static(filename):
    return static_file(filename, root='/home/mark/Documents/apache_thinkpad/pkppln/tools/views/js')

@route('/fonts/<filename:path>')
def server_static(filename):
    return static_file(filename, root='/home/mark/Documents/apache_thinkpad/pkppln/tools/views/fonts')

debug(True)
run(host='localhost', port=8080)

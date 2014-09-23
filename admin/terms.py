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
from datetime import datetime
from bottle import route, run, template, debug, static_file, request
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/opt/pkppln/config.cfg')

def get_term_details(id):
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'),
            cursorclass=MySQLdb.cursors.DictCursor)
        cur = con.cursor()
        cur.execute("SELECT * FROM terms_of_use WHERE id = %s", id)
        term = cur.fetchone()
        # Replace all non-UTF8 characters with U+FFFD, which will be visible in the text as a question mark.
        term['text'] = unicode(term['text'], 'utf-8', 'replace')
    except MySQLdb.Error, e:
        sys.exit(1)
    return term

@route('/list_terms')
def list_terms_of_use():
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        cur.execute("SELECT * FROM terms_of_use")
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
        term_values = {'id': None, 'language': '', 'key': '', 'text': ''}
    # If it's a clone of an existing one.
    else:
        form_title = 'Clone term of use'
        term_values = get_term_details(id)
    return template('crud_form', form_title=form_title, **term_values)

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
    return template('crud_form', form_title=form_title, **term_values)

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
        return template('messages', section='term_deleted', message='The term has been deleted.')
    else:
        return template('messages', section='term_not_deleted', message='Sorry, there was a problem deleting the term of use.')

@route('/insert_new_term', method='POST')
def insert_new_term_of_use():
    """
    We don't update rows in this application, we only add new ones.
    If request.headers.get('Referer') contains 'add_term/\d+', it's a clone;
    if it contains 'add_term/new', it's a new term; if it contains 'edit_term',
    it's a 'edit' (a new term and we need to set the current_version of the source 
    term to 'No').
    """
    language = request.forms.get('language').strip()
    key = request.forms.get('key').strip()
    text = request.forms.get('text').strip()
    text = unicode(text, 'utf8', 'replace')
    text = text.encode('utf8', 'replace')
    # id will be the string 'None' if it's a new term, and a string number if it's an existing term.
    id = request.forms.get('id')
    current_version = 'Yes'

    # If we are 'editing' a term, we need to set the current_version value of the original term
    # to 'No'.
    if re.findall(r"^[0-9]+$", id):
        try:
            con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
                config.get('Database', 'db_password'), config.get('Database', 'db_name'))
            cur = con.cursor()
            cur.execute("UPDATE terms_of_use SET current_version = 'No' WHERE id = %s", id)
            con.commit()
        except MySQLdb.Error, e:
            print e
            sys.exit(1)

    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        cur = con.cursor()
        # MySQL allows 'key' as a column name, but MySQLdb pukes on it. Wrapping it in backticks makes it taste better.
        cur.execute("INSERT INTO terms_of_use (current_version, last_updated, `key`, language, text) " +
            "VALUES(%s, %s, %s, %s, %s)", (current_version, datetime.now(), key, language, text))
        con.commit()
        # 'None' the str, not None the value.
        if id == 'None':
            return template('messages', section='term_added', message='The term of use has been added.')
        else:
            return template('messages', section='term_updated', message='The term of use has been updated.')
    except MySQLdb.Error, e:
        print e
        sys.exit(1)

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

# debug(True)
# run(host='localhost', port=8080)

"""
Generate atom, rss, and json feeds of new service terms.
"""

import sys
from os.path import abspath, isfile, dirname
import bottle
from bottle import route, run, template, response, HTTPResponse
import json
import pkppln


bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')


def mimetype(fmt):
    """
    Return the correct Mime type for a feed.
    """
    return {
        'atom': 'text/xml; charset=utf-8',
        'rss': 'text/xml; charset=utf-8',
        'json': 'application/json; charset=utf-8'
    }.get(fmt, 'text/plain')


@route('/feeds/')
def feeds_index():
    """
    Show a list of available feeds.
    """
    return template('feeds_index')


# options for feed: atom, rss, json
@route('/feeds/terms')
@route('/feeds/terms/<feed>')
def terms_feed(feed='atom'):
    """
    Generate a feed of the newest terms.
    """
    template_file = 'terms_' + feed
    template_path = dirname(__file__) + '/views/' + template_file + '.tpl'
    if not isfile(template_path):
        return HTTPResponse(status=404)
    mysql = pkppln.get_connection()
    cursor = mysql.cursor()
    cursor.execute(
        'SELECT * FROM terms_of_use ORDER BY last_updated DESC LIMIT 10'
    )
    terms = list(cursor.fetchall())
    response.content_type = mimetype(feed)
    return template(template_file, encoding='utf8', terms=terms, json=json)

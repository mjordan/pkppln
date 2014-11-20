"""
"""

import os
import sys
from os.path import abspath, isfile, dirname
import bottle
from bottle import route, run, template, response, HTTPResponse
import ConfigParser
import MySQLdb.cursors

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')
application = bottle.default_app()


def get_config():
    config_path = dirname(dirname(abspath(__file__))) + '/config.cfg'
    config = ConfigParser.ConfigParser()
    success = config.read(config_path)
    if config_path not in success:
        raise Exception('Cannot load config file ' + config_path)
    return config


def get_connection():
    config = get_config()
    con = MySQLdb.connect(
        host=config.get('Database', 'db_host'),
        user=config.get('Database', 'db_user'),
        passwd=config.get('Database', 'db_password'),
        db=config.get('Database', 'db_name'),
        cursorclass=MySQLdb.cursors.DictCursor
    )
    return con.cursor()


def mimetype(fmt):
    return {
        'atom': 'text/xml',
        'rss': 'text/xml',
        'json': 'application/json'
    }.get(fmt, 'text/plain')

# options for feed: atom, rss, json
@route('/terms')
@route('/terms/<feed>')
def terms_feed(feed='atom'):
    template_file = 'terms_' + feed
    template_path = dirname(__file__) + '/views/' + template_file + '.tpl'
    if not isfile(template_path):
        return HTTPResponse(status=404)
    cursor = get_connection()
    cursor.execute('SELECT * FROM terms_of_use ORDER BY last_updated DESC LIMIT 10')
    terms = list(cursor.fetchall())
    response.content_type = mimetype(feed)
    return template(template_file, terms=terms)


if __name__ == '__main__':
    bottle.debug(True)
    run(application, host='127.0.0.1', port=8080, reloader=True)

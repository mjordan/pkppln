"""
Generate atom, rss, and json feeds of new service terms.
"""

from os.path import abspath, isfile, dirname
import bottle
from bottle import route, run, template, response, HTTPResponse
import ConfigParser
import MySQLdb.cursors
import json

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')
application = bottle.default_app()


def get_config():
    """
    Get a configuration object for the application.
    """
    config_path = dirname(dirname(abspath(__file__))) + '/config.cfg'
    config = ConfigParser.ConfigParser()
    success = config.read(config_path)
    if config_path not in success:
        raise Exception('Cannot load config file ' + config_path)
    return config


def get_connection():
    """
    Connect to the database and return a cursor.
    """
    config = get_config()
    con = MySQLdb.connect(
        host=config.get('Database', 'db_host'),
        user=config.get('Database', 'db_user'),
        passwd=config.get('Database', 'db_password'),
        db=config.get('Database', 'db_name'),
        cursorclass=MySQLdb.cursors.DictCursor,
        use_unicode=True,
        charset="utf8"
    )
    return con.cursor()


def mimetype(fmt):
    """
    Return the correct Mime type for a feed.
    """
    return {
        'atom': 'text/xml; charset=utf-8',
        'rss': 'text/xml; charset=utf-8',
        'json': 'application/json; charset=utf-8'
    }.get(fmt, 'text/plain')


# options for feed: atom, rss, json
@route('/terms')
@route('/terms/<feed>')
def terms_feed(feed='atom'):
    """
    Generate a feed of the newest terms.
    """
    template_file = 'terms_' + feed
    template_path = dirname(__file__) + '/views/' + template_file + '.tpl'
    if not isfile(template_path):
        return HTTPResponse(status=404)
    cursor = get_connection()
    cursor.execute(
        'SELECT * FROM terms_of_use ORDER BY last_updated DESC LIMIT 10'
    )
    terms = list(cursor.fetchall())
    response.content_type = mimetype(feed)
    return template(template_file, encoding='utf8', terms=terms, json=json)


if __name__ == '__main__':
    bottle.debug(True)
    run(application, host='127.0.0.1', port=8080, reloader=True)

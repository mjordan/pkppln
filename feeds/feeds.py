"""
"""

import bottle
from bottle import route, static_file, run, template
import ConfigParser
import MySQLdb
import MySQLdb.cursors

application = bottle.default_app()

config = ConfigParser.ConfigParser()
config.read('/opt/pkppln/config.cfg')


@route('/')
def feeds_list():
    return 'hello world.'


def get_connection():
    con = MySQLdb.connect(
        host=config.get('Database', 'db_host'),
        user=config.get('Database', 'db_user'),
        passwd=config.get('Database', 'db_password'),
        db=config.get('Database', 'db_name'),
        cursorclass=MySQLdb.cursors.DictCursor
    )
    return con.cursor()


# options for feed: atom, rss, json
@route('/terms')
@route('/terms/<feed>')
def terms_feed(feed='atom'):
    cursor = get_connection()
    cursor.execute('SELECT * FROM terms_of_use ORDER BY last_updated DESC LIMIT 10')
    terms = list(cursor.fetchall())
    return template('terms_' + feed, terms=terms)


# Routes for static files - CSS, Javascript, etc.
# @route('/css/<filename:path>')
def static_css(filename):
    return static_file(filename, root='/var/www/html/css')


# @route('/js/<filename:path>')
def static_js(filename):
    return static_file(filename, root='/var/www/html/js')


# @route('/fonts/<filename:path>')
def static_fonts(filename):
    return static_file(filename, root='/var/www/html/fonts')

bottle.debug(True)
run(application, host='localhost', port=8080, reloader=True)

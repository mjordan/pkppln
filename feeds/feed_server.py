"""
"""

import os
import bottle
from bottle import route, run, template
import ConfigParser
import MySQLdb.cursors

application = bottle.default_app()

config = ConfigParser.ConfigParser()
config.read('/opt/pkppln/config.cfg')


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
    template_file = 'terms_' + feed
    cursor = get_connection()
    cursor.execute('SELECT * FROM terms_of_use ORDER BY last_updated DESC LIMIT 10')
    terms = list(cursor.fetchall())
    bottle.TEMPLATE_PATH.insert(0, os.path.dirname(__file__) + '/views')
    return template(template_file, terms=terms)


if __name__ == '__main__':
    bottle.debug(True)
    run(application, host='localhost', port=8080, reloader=True)

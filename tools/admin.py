import MySQLdb
import MySQLdb.cursors
from bottle import route, run, template, debug, static_file
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/home/mark/Documents/apache_thinkpad/pkppln/config_dev.cfg')

@route('/list_terms')
def list_terms_of_use():
    language = 'en-US'
    try:
        con = MySQLdb.connect(config.get('Database', 'db_host'), config.get('Database', 'db_user'),
            config.get('Database', 'db_password'), config.get('Database', 'db_name'))
        terms_of_use_cur = con.cursor()
        terms_of_use_cur.execute("SELECT * FROM terms_of_use WHERE language = %s and last_updated = (SELECT max(last_updated) FROM terms_of_use)", language)
        result = terms_of_use_cur.fetchall()
    except MySQLdb.Error, e:
        sys.exit(1)

    return template('list_terms_of_use', rows=result)

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

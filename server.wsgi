
import os
import sys
import bottle
from os.path import abspath, dirname
from bottle import run, get, static_file

sys.path.append(dirname(abspath(__file__)))

import webapp.admin.terms_server
import webapp.feeds.feed_server
import webapp.sword.sword_server

application = bottle.default_app()

@get('/css/<filename:path>')
def static_css(filename):
    return static_file(filename, dirname(abspath(__file__)) + '/css/')


@get('/js/<filename:path>')
def static_js(filename):
    return static_file(filename, dirname(abspath(__file__)) + '/js/')


@get('/fonts/<filename:path>')
def static_fonts(filename):
    return static_file(filename, dirname(abspath(__file__)) + '/fonts/')

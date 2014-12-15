#!/usr/bin/env python

import sys

import bottle
from os.path import abspath, dirname
from bottle import run, get, static_file

sys.path.append(dirname(abspath(__file__)))

import pkppln
import webapp.feeds.feed_server
import webapp.sword.sword_server
import webapp.admin.terms_server

application = bottle.default_app()


# Routes for static files - CSS, Javascript, etc.
@get('/css/<filename:path>')
def static_css(filename):
    return static_file(filename, dirname(abspath(__file__)) + '/css/')


@get('/js/<filename:path>')
def static_js(filename):
    return static_file(filename, dirname(abspath(__file__)) + '/js/')


@get('/fonts/<filename:path>')
def static_fonts(filename):
    return static_file(filename, dirname(abspath(__file__)) + '/fonts/')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        pkppln.config_file_name = sys.argv[1]
    bottle.debug(True)
    run(application, host='127.0.0.1', port=8080, reloader=True)

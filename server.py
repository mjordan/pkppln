#!/usr/bin/env python

import sys
import bottle
from bottle import Bottle, request, error, response, Response
from os.path import abspath, dirname
import pkppln
import logging
from webapp.admin.terms_server import TermsApp
from webapp.sword.sword_server import SwordServer
from webapp.static.static_server import StaticApp
from webapp.feeds.feed_server import FeedsApp
from webapp.admin.journal_server import JournalsApp


def after_request():
    if request.path.startswith('/static'):
        return

    try:
        route_name = request.route.callback.__name__
    except:
        route_name = '(unknown)'

    try:
        pkppln.log_message(" - ".join([
            'finished', request.get('REMOTE_ADDR'),
            request.method, request.path,
            type(request.app).__name__ + "#" + route_name
        ]), logging.INFO)
    except:
        pass


def before_request():
    #     pkppln.log_message(" - ".join([
    #         'starting', request.get('REMOTE_ADDR'),
    #         request.method, request.path]))
    pkppln.initialize()


static_path = dirname(abspath(__file__)) + '/static'

app = bottle.default_app()
app.add_hook('before_request', before_request)
app.add_hook('after_request', after_request)
app.mount('/static/', StaticApp('Static', static_path))
app.mount('/admin/terms/', TermsApp('Terms'))
app.mount('/admin/journals/', JournalsApp('JournalsApp'))
app.mount('/feeds/', FeedsApp('Feeds'))
app.mount('/api/sword/2.0/', SwordServer('SWORD'))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        pkppln.config_file_name = sys.argv[1]
    bottle.debug(True)
    app.run(host='127.0.0.1', port=9999, reloader=True)

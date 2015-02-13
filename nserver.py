#!/usr/bin/env python

import sys
import bottle
from bottle import request, error
from os.path import abspath, dirname
import pkppln
import logging
from webapp.admin.terms_server import TermsApp
from webapp.static.static_server import StaticApp


def after_request():
    if request.path.startswith('/static'):
        return
    pkppln.log_message(" - ".join([
        'request', request.get('REMOTE_ADDR'), request.method, request.path,
        request.app.__class__.__name__ + "#" + request.route.callback.__name__
    ]), logging.INFO)

static_path = dirname(abspath(__file__)) + '/static'

app = bottle.default_app()
app.add_hook('after_request', after_request)
app.mount('/static/', StaticApp('Static', static_path))
app.mount('/admin/terms/', TermsApp('Terms'))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        pkppln.config_file_name = sys.argv[1]
    bottle.debug(True)
    app.run(host='127.0.0.1', port=9999, reloader=True)

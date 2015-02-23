"""
Generate atom, rss, and json feeds of new service terms.
"""

from os.path import isfile, dirname
import bottle
from bottle import template, request, response, HTTPResponse
import json
import pkppln


bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')


from webapp.webapp import WebApp


class FeedsApp(WebApp):

    def __init__(self, name):
        WebApp.__init__(self, name)
        self.route('/', method='GET', callback=self.feeds_index)
        self.route('/terms/', method='GET', callback=self.terms_feed)
        self.route('/terms/<feed>', method='GET', callback=self.terms_feed)

    def mimetype(self, fmt):
        """
        Return the correct Mime type for a feed.
        """
        return {
            'atom': 'text/xml; charset=utf-8',
            'rss': 'text/xml; charset=utf-8',
            'json': 'application/json; charset=utf-8'
        }.get(fmt, 'text/plain')

    def feeds_index(self):
        """
        Show a list of available feeds.
        """
        return template('feeds_index')

    def terms_feed(self, feed='atom', accept=None):
        """
        Generate a feed of the newest terms.
        """
        language = self.get_request_lang(accept)

        # @TODO language needs to be processed a bit:
        # en-CA,en;q=0.8,en-GB;q=0.6,en-US;q=0.4
        handle = pkppln.get_connection();

        template_file = 'terms_' + feed
        template_path = dirname(__file__) + '/views/' + template_file + '.tpl'
        if not isfile(template_path):
            return HTTPResponse(status=404)
        terms = pkppln.get_all_terms(language, db=handle)
        response.content_type = self.mimetype(feed)
        return template(template_file, encoding='utf8', terms=terms, 
                        json=json, language=language)

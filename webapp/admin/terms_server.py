"""
Simple CRUD tool for PKP PLN terms of use.

Copyright (c) 2014-2015 Simon Fraser University Library
Copyright (c) 2014-2015 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

# @todo Add filters to routes as per http://bottlepy.org/docs/dev/routing.html

from os.path import dirname
from bottle import Bottle, request, template
import bottle
import pkppln

bottle.TEMPLATE_PATH.insert(0, dirname(__file__) + '/views')

from webapp.webapp import WebApp


class TermsApp(WebApp):

    def __init__(self, name):
        WebApp.__init__(self, "TermsApp")
        self.route('/', method='GET', callback=self.terms_list)
        self.route('/list', method='GET', callback=self.terms_list)
        self.route('/list_terms', method='GET', callback=self.terms_list)
        self.route('/detail/:key_code', method='GET', callback=self.term_detail)
        self.route('/sort', method='GET', callback=self.terms_sort)
        self.route('/sort', method='POST', callback=self.terms_sort_save)
        self.route('/translate', method='GET', callback=self.terms_translate)
        self.route('/translate', method='POST', callback=self.terms_translate_save)
        self.route('/add_term', method='GET', callback=self.add_term)
        self.route('/edit_term/:key_code', method='GET', callback=self.edit_term)
        self.route('/edit_term/:key_code/:lang_code', method='GET', callback=self.edit_term)
        self.route('/save', method='POST', callback=self.save_term)

    def terms_list(self):
        """Show all the terms."""
        lang = request.query.lang or 'en-US'
        handle = pkppln.get_connection()
        terms = pkppln.get_all_terms(lang, db=handle)
        languages = pkppln.get_term_languages(db=handle)

        if len(terms):
            return template('terms_list', languages=languages,
                            display_lang=lang, terms=terms)
        else:
            return template('messages', section='no_terms', display_lang=lang,
                            message='Sorry, there are no terms of use.')

    def term_detail(self, key_code):
        terms = pkppln.get_terms_key(key_code)
        return template('term_detail', terms=terms, key_code=key_code)

    def terms_sort(self):
        """Show all the terms."""
        handle = pkppln.get_connection()
        terms = pkppln.get_all_terms(db=handle)
        return template('terms_sort', terms=terms, message=None)

    def terms_sort_save(self):
        handle = pkppln.get_connection()
        term_order = request.forms.get('order').split(',')
        for idx, key in enumerate(term_order):
            terms = pkppln.get_terms_key(key, db=handle)
            for term in terms:
                term['weight'] = idx
                try:
                    pkppln.update_term(term, db=handle)
                except:
                    handle.rollback()
                    raise
        handle.commit()
        terms = pkppln.get_all_terms(db=handle)
        return template('terms_sort', terms=terms, message="Saved")

    def terms_translate(self):
        """Show all the terms."""
        handle = pkppln.get_connection()
        lang = request.query.lang
        terms = pkppln.get_all_terms(lang, db=handle)
        en_terms = {}
        for t in pkppln.get_all_terms('en-US', db=handle):
            en_terms[t['key_code']] = t

        return template('terms_translate', terms=terms, en_terms=en_terms,
                        display_lang=lang, message=None)

    def terms_translate_save(self):
        """Show all the terms."""
        lang = request.forms.get('display_lang')
        handle = pkppln.get_connection()
        terms = pkppln.get_all_terms(lang, db=handle)
        for term in terms:
            content = request.forms.get(term['key_code'], '').strip()
            if content == '':
                continue
            term['lang_code'] = lang
            term['content'] = content
            try:
                pkppln.edit_term(term, db=handle)
            except:
                handle.rollback()
                raise
        en_terms = {}
        handle.commit()
        for t in pkppln.get_all_terms('en-US', handle):
            en_terms[t['key_code']] = t

        return template('terms_translate', terms=terms, en_terms=en_terms,
                        display_lang=lang, message='Translation saved.')

    def add_term(self, term_id=''):
        """Add a new term."""
        term = {'lang_code': 'en-US', 'key_code': '', 'content': ''}
        return template('terms_form', form_title='Create a new Term', **term)

    def edit_term(self, key_code, lang_code='en-us'):
        """We need to keep all versions of each term of use."""
        handle = pkppln.get_connection()
        form_title = 'Edit term of use'
        term = pkppln.get_term(key_code, lang_code, db=handle)
        if term is None:
            return template('messages',
                            message='That term does not exist.')
        if term['lang_code'] != lang_code:
            return template('messages',
                            message='The term does not exist in that language.')
        return template('terms_form', action='edit',
                        form_title=form_title, **term)

    def save_term(self):
        """
        """
        term = {}
        term['lang_code'] = request.forms.get('language').strip()
        term['key_code'] = request.forms.get('key').strip()
        term['content'] = request.forms.get('text').strip()
        term['id'] = request.forms.get('id', '').strip()
        term['weight'] = request.forms.get('weight', '1').strip()
        handle = pkppln.get_connection()
        try:
            pkppln.edit_term(term, handle)
        except:
            handle.rollback()
            raise
        handle.commit()
        return template('messages',
                        message='A new version of the term has been saved.')

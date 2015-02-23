from bottle import Bottle, request
import pkppln


class WebApp(Bottle):

    def __init__(self, name):
        Bottle.__init__(self)
        self.name = name

    def get_request_lang(self, header=None):
        if header is None:
            header = request.headers.get('Accept-Language', None)
        if header is None:
            return 'en-US'
        locales = [locale.split(';')[0].strip() for locale in header.split(',')]
        available = [lang['lang_code'] for lang in pkppln.get_term_languages()]

        for locale in locales:
            if locale in available:
                return locale
        return 'en-US'

    def get_name(self):
        return self.name

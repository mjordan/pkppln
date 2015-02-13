from bottle import static_file
from webapp.webapp import WebApp
import pkppln


class StaticApp(WebApp):

    def __init__(self, name, static_path):
        super(StaticApp, self).__init__(name)
        self.static_path = static_path
        self.route('/css/:filename', callback=self.static_css)
        self.route('/js/:filename', callback=self.static_js)
        self.route('/fonts/:filename', callback=self.static_fonts)

    def static_css(self, filename):
        return static_file(filename, self.static_path + '/css/')

    def static_js(self, filename):
        return static_file(filename, self.static_path + '/js/')

    def static_fonts(self, filename):
        return static_file(filename, self.static_path + '/font/')

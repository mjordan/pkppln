from bottle import Bottle

class WebApp(Bottle):

    def __init__(self, name):
        super(WebApp, self).__init__()
        self.name = name

    def get_name(self):
        return self.name

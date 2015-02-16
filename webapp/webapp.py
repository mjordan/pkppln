from bottle import Bottle


class WebApp(Bottle):

    def __init__(self, name):
        Bottle.__init__(self)
        self.name = name

    def get_name(self):
        return self.name

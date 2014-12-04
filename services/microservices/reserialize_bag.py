from services.PlnService import PlnService


class ReserializeBag(PlnService):

    def state_before(self):
        return 'contentValidated'

    def state_after(self):
        return 'reserialized'

    def execute(self, deposit):
        return '', ''

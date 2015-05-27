from commands.PlnCommand import PlnCommand


class ListServices(PlnCommand):

    def description(self):
        return "List the services in the order they should be run."

    def services(self):
        return [
            'harvest',
            'validate_payload',
            'validate_bag',
            'virus_check',
            'validate_export',
            'reserialize_bag',
            'stage_bag',
            'deposit_to_pln',
            'check_status'
        ]

    def execute(self, args):
        self.output(
            0, 'usage: pln-service.py [-h] [-v | -q] [ -n | -f ] service ...')
        self.output(0, 'where service is one of ')
        for f in self.services():
            self.output(0, '  ' + f)

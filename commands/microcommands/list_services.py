from commands.PlnCommand import PlnCommand


class ListServices(PlnCommand):

    def execute(self, args):
        output = 'usage: pln-service.py [-h] [-v | -q] service ...\n'
        output += 'where service is one of \n'
        for f in ['harvest', 'validate_payload', 'validate_bag', 'virus_check',
                  'validate_export', 'reserialize_bag', 'stage_bag',
                  'deposit_to_pln', 'check_status']:
            output += '  ' + f + '\n'
        return output

import pkppln
from commands.PlnCommand import PlnCommand


class ListDeposits(PlnCommand):

    def add_args(self, parser):
        parser.add_argument(
            '--state',
            help='Only show deposits with this state'
        )
        parser.add_argument(
            '--outcome',
            help='Only show deposits with this outcome'
        )

    def description(self):
        return "List all deposits in the staging service."

    def execute(self, args):
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            'select deposit_uuid, processing_state, outcome from deposits')
        deposits = cursor.fetchall()
        output = ''
        for deposit in deposits:
            if args.state is not None and deposit['processing_state'] != args.state:
                continue
            if args.outcome is not None and deposit['outcome'] != args.outcome:
                continue
            output += '\t'.join((deposit['deposit_uuid'],
                                 deposit['processing_state'],
                                 deposit['outcome']))
            output += '\n'
        return output

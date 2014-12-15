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

    def execute(self, args):
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            'select deposit_uuid, processing_state, outcome from deposits')
        deposits = cursor.fetchall()
        for deposit in deposits:
            if args.state and deposit['processing_state'] != args.state:
                continue
            if args.outcome and deposit['outcome'] != args.outcome:
                continue
            print '\t'.join((deposit['deposit_uuid'],
                             deposit['processing_state'],
                             deposit['outcome']))

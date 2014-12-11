import pkppln
from commands.PlnCommand import PlnCommand


class ServiceLog(PlnCommand):

    """Report all the activity on a deposit."""

    def add_args(self, parser):
        parser.add_argument(
            'deposit',
            help='Deposit to query'
        )
        parser.add_argument(
            '-v', '--verbose',
            help='Show verbose output',
            action='store_true'
        )

    def description(self):
        return "Report all processing steps for a deposit."

    def execute(self, args):
        deposit = args.deposit
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            'select * from microservices where deposit_uuid=%s',
            [deposit]
        )
        entries = cursor.fetchall()
        print '{0:<18} {1:<20} {2:<20} {3:<10}'.format(
            'Service', 'Started', 'Finished', 'Outcome')
        for entry in entries:
            print '{0:<18} {1:<20} {2:<20} {3:<10}'.format(
                entry['microservice'], str(entry['started_on']),
                str(entry['finished_on']), entry['outcome'])
            if entry['error'] and args.verbose:
                print entry['error']

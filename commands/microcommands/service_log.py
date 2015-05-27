import pkppln
from commands.PlnCommand import PlnCommand


class ServiceLog(PlnCommand):

    """Report all the activity on a deposit."""

    def add_args(self, parser):
        parser.add_argument(
            'deposit',
            help='Deposit to query'
        )

    def description(self):
        return "Report all processing steps for a deposit."

    def execute(self, args):
        deposit = args.deposit
        entries = pkppln.db_query(
            'select * from microservices where deposit_uuid=%s',
            [deposit]
        )
        self.output(0, '{0:<18} {1:<20} {2:<20} {3:<10}'.format(
            'Service', 'Started', 'Finished', 'Outcome'))

        for entry in entries:
            self.output(0, '{0:<18} {1:<20} {2:<20} {3:<10}'.format(
                entry['microservice'], str(entry['started_on']),
                str(entry['finished_on']), entry['outcome']))

            if entry['error']:
                self.output(1, entry['error'])

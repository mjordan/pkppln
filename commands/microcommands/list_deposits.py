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
        deposits = pkppln.db_query(
            'select * from deposits')

        for deposit in deposits:
            if args.state is not None and deposit['processing_state'] != args.state:
                continue
            if args.outcome is not None and deposit['outcome'] != args.outcome:
                continue
            self.output(0, '\t'.join((deposit['file_uuid'],
                                      deposit['processing_state'],
                                      deposit['outcome'])))

from datetime import datetime
import pkppln
from commands.PlnCommand import PlnCommand
import traceback


class ResetDeposit(PlnCommand):

    """Set the state of a deposit, so that it may be reprocessed or
    have a processing step skipped."""

    def add_args(self, parser):
        parser.add_argument(
            'uuid',
            help='Deposit UUID'
        )
        parser.add_argument(
            'state',
            help='State to set the deposit to'
        )

    def description(self):
        return "Reset processing state of a deposit."

    def execute(self, args):
        try:
            pkppln.update_deposit(args.uuid, args.state,
                                  'reset', db=self.handle)
            pkppln.log_microservice(args.state, args.uuid, datetime.now(),
                                    datetime.now(), 'reset', '',
                                    db=self.handle)
        except Exception as e:
            self.handle.rollback()
            raise
        self.handle.commit()

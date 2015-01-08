from datetime import datetime
import pkppln
from commands.PlnCommand import PlnCommand


class ResetDeposit(PlnCommand):

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
        mysql = pkppln.get_connection()

        update = pkppln.update_deposit(args.uuid, args.state, 'reset')
        log = pkppln.log_microservice(args.state, args.uuid, datetime.now(),
                                      datetime.now(), 'reset', '')

        if update and log:
            mysql.commit()
            return ''

        mysql.rollback()
        return "Failed.\n  Update: " + str(update) + "\n  log: " + str(log)

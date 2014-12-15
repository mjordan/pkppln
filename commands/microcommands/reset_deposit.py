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

    def execute(self, args):
        mysql = pkppln.get_connection()

        update = pkppln.update_deposit(args.uuid, args.state, 'reset')
        log = pkppln.log_microservice(args.state, args.uuid, datetime.now(),
                                      datetime.now(), 'reset', '')

        if update and log:
            mysql.commit()
            return

        mysql.rollback()
        print "Failed."
        print "Update: ", update, " log: ", log

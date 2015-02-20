import pkppln
from commands.PlnCommand import PlnCommand


class JournalHistory(PlnCommand):

    def add_args(self, parser):
        parser.add_argument(
            'uuid',
            help='Journal UUID'
        )

    def description(self):
        return "Report all deposits for a journal."

    def execute(self, args):
        uuid = args.uuid
        deposits = pkppln.get_journal_deposits(uuid)
        if len(deposits) == 0:
            deposit = pkppln.get_deposit(uuid)
            if deposit is not None:
                deposits = pkppln.get_journal_deposits(deposit['journal_uuid'])
        if len(deposits) == 0:
            self.output(0, 'No journal found.')
            return

        for deposit in deposits:
            self.output(0, 'UUID: ' + deposit['deposit_uuid'])
            self.output(0, 'Date: ' + str(deposit['date_deposited']))
            self.output(0, 'Vol/Issue: ' + deposit['deposit_volume'] + '/' + deposit['deposit_issue'])
            self.output(0, 'URL: ' + deposit['deposit_url'])
            self.output(0, 'State: ' + deposit['processing_state'])
            self.output(0, 'Pln State: ' + deposit['pln_state'])
            self.output(0, ' ')

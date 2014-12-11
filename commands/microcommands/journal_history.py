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
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            'select * from journals where journal_uuid=%s',
            [uuid]
        )
        entries = cursor.fetchall()
        if len(entries) == 0:
            cursor.execute(
                'SELECT * FROM journals WHERE deposit_uuid=%s',
                [uuid]
            )
            journal = cursor.fetchone()
            if journal:
                cursor.execute('SELECT * FROM JOURNALS WHERE journal_uuid=%s',
                               [journal['journal_uuid']])
                entries = cursor.fetchall()

        if len(entries) == 0:
            return 'No journal found.'

        output = '\t'.join([
            'Title', 'ISSN', 'URL', 'Email', 'Deposit', 'Date'
        ])
        output += '\n'
        for entry in entries:
            output += '\t'.join([entry['title'], entry['issn'],
                                 entry['journal_url'], entry['contact_email'],
                                 entry['deposit_uuid'],
                                 str(entry['date_deposited'])])
            output += '\n'
        return output

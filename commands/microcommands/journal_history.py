import pkppln
from commands.PlnCommand import PlnCommand


class JournalHistory(PlnCommand):

    def add_args(self, parser):
        parser.add_argument(
            'uuid',
            help='Journal UUID'
        )

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
            deposit = pkppln.get_deposit(uuid)
            if deposit:
                cursor.execute('SELECT * FROM JOURNALS WHERE journal_uuid=%s',
                               [deposit['journal_uuid']])
                entries = cursor.fetchall()

        if len(entries) == 0:
            print 'No journal found.'
            return

        print '\t'.join(['Title', 'ISSN', 'URL', 'Email', 'Deposit', 'Date'])
        for entry in entries:
            print '\t'.join([entry['title'], entry['issn'],
                             entry['journal_url'], entry['contact_email'],
                             entry['deposit_uuid'],
                             str(entry['date_deposited'])])

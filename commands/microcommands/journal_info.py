import pkppln
from commands.PlnCommand import PlnCommand


class JournalInfo(PlnCommand):

    def add_args(self, parser):
        parser.add_argument(
            'uuid',
            help='Journal UUID'
        )

    def get_journal_entries(self, uuid):
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            """select distinct journal_uuid, title, issn, journal_url,
            contact_email from journals where journal_uuid=%s""",
            [uuid]
        )
        return cursor.fetchall()

    def execute(self, args):
        uuid = args.uuid
        entries = self.get_journal_entries(uuid)
        if len(entries) == 0:
            deposit = pkppln.get_deposit(uuid)
            if deposit:
                entries = self.get_journal_entries(deposit['journal_uuid'])

        if len(entries) == 0:
            print 'No journal found.'
            return

        for entry in entries:
            print 'Title:     ', entry['title']
            print 'ISSN:      ', entry['issn']
            print 'URL:       ', entry['journal_url']
            print 'Email:     ', entry['contact_email']
            print

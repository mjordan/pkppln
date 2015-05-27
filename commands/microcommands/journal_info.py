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

    def description(self):
        return "Report all known journal metadata."

    def execute(self, args):
        uuid = args.uuid
        journal = pkppln.get_journal(uuid)
        if journal is None:
            deposit = pkppln.get_deposit(uuid)
            if deposit is not None:
                journal = pkppln.get_journal(deposit['journal_uuid'])

        if journal is None:
            self.output(0, 'No journal found.')
            return
        
        self.output(0, 'UUID:          ' + journal['journal_uuid'])
        self.output(0, 'Contact date:  ' + str(journal['contact_date']))
        self.output(0, 'Notified date: ' + str(journal['notified_date']))
        self.output(0, 'Title:         ' + journal['title'])
        self.output(0, 'ISSN:          ' + journal['issn'])
        self.output(0, 'URL:           ' + journal['journal_url'])
        self.output(0, 'Status:        ' + journal['journal_status'])
        self.output(0, 'Contact:       ' + journal['contact_email'])
        self.output(0, 'Publisher:     ' + journal['publisher_name'])
        self.output(0, 'Publisher:     ' + journal['publisher_url'])

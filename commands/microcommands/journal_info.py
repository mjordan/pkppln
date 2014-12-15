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
            mysql = pkppln.get_connection()
            cursor = mysql.cursor()
            cursor.execute(
                'SELECT * FROM journals WHERE deposit_uuid=%s',
                [uuid]
            )
            journal = cursor.fetchone()
            if journal:
                entries = self.get_journal_entries(journal['journal_uuid'])

        if len(entries) == 0:
            return 'No journal found.'

        output = ''
        for entry in entries:
            output += 'Title:     ' + entry['title'] + '\n'
            output += 'ISSN:      ' + entry['issn'] + '\n'
            output += 'URL:       ' + entry['journal_url'] + '\n'
            output += 'Email:     ' + entry['contact_email'] + '\n'
            output += '\n'

        return output

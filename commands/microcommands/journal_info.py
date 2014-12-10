import pkppln
from commands.PlnCommand import PlnCommand


class JournalInfo(PlnCommand):

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
            'select distinct journal_uuid, title, issn, journal_url, contact_email from journals where journal_uuid=%s',
            [uuid]
        )
        entries = cursor.fetchall()
        for entry in entries:
            print 'Title:     ', entry['title']
            print 'ISSN:      ', entry['issn']
            print 'URL:       ', entry['journal_url']
            print 'Email:     ', entry['contact_email']
            print

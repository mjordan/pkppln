import pkppln
from commands.PlnCommand import PlnCommand


class ListJournals(PlnCommand):

    def description(self):
        return "Report all journals that have made a deposit."

    def execute(self, args):
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            '''select title, journal_url, publisher_name, publisher_url,
            max(date_deposited) as recent_deposit, journal_uuid
            from journals
            group by title, journal_url, journal_uuid, publisher_name,
                publisher_url
            ''')
        journals = cursor.fetchall()
        output = ''
        for journal in journals:
            output += '\t'.join((
                journal['title'], journal['journal_url'],
                journal['publisher_name'], journal['publisher_url'],
                str(journal['recent_deposit']),
                journal['journal_uuid']))
            output += '\n'
        return output

import pkppln
from commands.PlnCommand import PlnCommand


class ListJournals(PlnCommand):

    def execute(self, args):
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        cursor.execute(
            '''select title, journal_url,
                        max(date_deposited) as recent_deposit, journal_uuid
                from mypln.journals
                group by title, journal_url, journal_uuid
                ''')
        journals = cursor.fetchall()
        output = ''
        for journal in journals:
            output += '\t'.join((journal['title'], journal['journal_url'],
                                 str(journal['recent_deposit']),
                                 journal['journal_uuid']))
            output += '\n'
        return output

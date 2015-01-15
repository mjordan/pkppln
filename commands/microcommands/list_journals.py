import pkppln
from commands.PlnCommand import PlnCommand


class ListJournals(PlnCommand):

    def description(self):
        return "Report all journals that have made a deposit."

    def execute(self, args):
        journals = pkppln.get_journals()
        output = ''
        for journal in journals:
            output += '\t'.join((
                journal['title'], journal['journal_url'],
                journal['publisher_name'], journal['publisher_url'],
                str(journal['recent_deposit']),
                journal['journal_uuid']))
            output += '\n'
        return output

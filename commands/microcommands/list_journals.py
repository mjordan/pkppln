import pkppln
from commands.PlnCommand import PlnCommand


class ListJournals(PlnCommand):

    def description(self):
        return "Report all journals that have made a deposit."

    def execute(self, args):
        journals = pkppln.get_journals()

        for journal in journals:
            self.output(0, '\t'.join((
                journal['title'], journal['journal_url'],
                journal['journal_uuid'])))

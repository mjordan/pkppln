import datetime
import requests
import pkppln
from commands.PlnCommand import PlnCommand
import smtplib
from email.mime.text import MIMEText
from lxml import etree
from itertools import izip_longest

dtd = etree.DTD('ping.dtd')


class HealthCheck(PlnCommand):

    def __init__(self):
        super(HealthCheck, self).__init__()
        self.bad_journals = []
        self.good_journals = []

    def description(self):
        return "Check journal health and notify admin."

    def add_bad_journal(self, journal, reason, exception=None):
        journal['reason'] = reason
        if exception is not None:
            journal['reason'] += '\n' + str(exception)
        self.bad_journals.append(journal)

    def send_notification(self):
        msg = '''
The PKP PLN staging server has lost contact with one or more journals listed
below. Please contact the journal managers to decide if the journal should be
triggered.'''

        for journal in self.bad_journals:
            msg += '\n\n ---- \n\n'
            msg += 'Title: ' + journal['title'] + '\n'
            msg += 'ISSN: ' + journal['issn'] + '\n'
            msg += 'Contact: ' + journal['contact_email'] + '\n' 
            msg += 'Journal Url: ' + journal['journal_url'] + '\n'
            msg += 'Publisher: ' + journal['publisher_name'] + '\n'
            msg += 'Most recent contact: ' + str(journal['contact_date']) + '\n'
            msg += journal['reason']

        print msg

    def process_journal(self, journal):
        url = journal['journal_url']
        if not url.endswith('/'):
            url = url + '/'
        url = url + 'gateway/plugin/PLNGatewayPlugin'

        try:
            r = requests.get(url)
        except Exception as e:
            self.add_bad_journal(
                journal,
                'Cannot reach journal.',
                exception=e
            )
            return

        if r.status_code != 200:
            self.add_bad_journal(
                journal,
                'Bad response code ' + str(r.status_code) + ' ' + r.reason
            )
            return

        try:
            root = etree.XML(r.content)
        except Exception as e:
            self.add_bad_journal(
                journal,
                'The XML response from the journal could not be processed.',
                exception=e
            )
            return

        if dtd.validate(root) is False:
            self.add_bad_journal(
                journal,
                'The XML response from the journal does not validate'
            )
            return
        self.good_journals.append(journal)

    def execute(self, args):
        config = pkppln.get_config()
        frequency = config.get('JournalHealth', 'minimum_frequency')
        journals = pkppln.db_query(
            'SELECT * FROM journals WHERE datediff(now(), contact_date) > %s',
            [frequency]
        )
        if len(journals) == 0:
            return
        for journal in journals:
            self.process_journal(journal)

        if len(self.bad_journals) > 0:
            self.send_notification()

        for journal in self.good_journals:
            journal['journal_status'] = 'healthy'
            journal['contact_date'] = datetime.datetime.now()
            pkppln.update_journal(journal, db=self.handle)

        self.handle.commit()

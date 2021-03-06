import pkppln
from commands.PlnCommand import PlnCommand
from lxml import etree as et
from lxml.builder import ElementMaker
from datetime import datetime

E = ElementMaker(
    namespace=pkppln.namespaces['oph'],
    nsmap=pkppln.namespaces
)


class GenerateOnix(PlnCommand):

    def description(self):
        return "Generate ONIX-PH XML."

    def skeleton(self):
        """Create the skeleton of an ONIX xml document."""
        onix = E.ONIXPreservationHoldings(
            E.Header(
                E.Sender(
                    E.SenderName('Public Knowledge Project PLN')
                ),
                E.SentDateTime(
                    datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                ),
                E.CompleteFile()
            ),
            {
                # set the schema location. unfortunately ElementMaker doesn't
                # understand prefixed attribute names.
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': '',
                'version': '0.2'
            }
        )

        holdingsList = E.HoldingsList(
            E.PreservationAgency(
                E.PreservationAgencyName('Public Knowledge Project PLN')
            )
        )
        onix.append(holdingsList)
        return onix, holdingsList

    def addDeposit(self, deposit):
        """Create a PackageDetail element and return it. Called once for
        each deposit in the system."""
        element = E.PackageDetail(
            E.Coverage(
                # item-by-item
                E.CoverageDescriptionLevel('03'),
                E.SupplementInclusion('04'),
                E.IndexInclusion('04'),
                E.FixedCoverage(
                    E.Release(
                        E.Enumeration(
                            E.Level1(
                                E.Unit('Volume'),
                                E.Number(deposit['deposit_volume'])
                            ),
                            E.Level2(
                                E.Unit('Issue'),
                                E.Number(deposit['deposit_issue'])
                            )
                        ),
                        E.NominalDate(
                            E.Calendar('00'),
                            E.DateFormat('00'),
                            E.Date(deposit['deposit_pubdate'].replace('-', ''))
                        )
                    )
                )
            ),
            E.PreservationStatus(
                E.PreservationStatusCode('05'),
                E.DateOfStatus(deposit['deposited_lom'].strftime('%Y%m%d')),
            ),
            E.VerificationStatus('01'),
        )
        return element

    def addAllDeposits(self, journal, deposits):
        """Add all deposits to the xml. Each one is wrapped in an OnlinePackage
        element."""
        element = E.OnlinePackage(
            E.Website(
                E.WebsiteRole('05'),
                E.WebsiteLink(journal['journal_url'])
            )
        )
        for deposit in deposits:
            element.append(self.addDeposit(deposit))
        return element

    def addJournals(self, holdingsList):
        """Add all the journals to the xml."""
        for journal in pkppln.get_journals():
            # THIS FUNCTION HAS CHANGED.
            all_deposits = pkppln.get_journal_deposits(
                journal['journal_uuid'],
            )
            deposits = [x for x in all_deposits if x['processing_state'] == 'deposited']
            if len(deposits) == 0:
                continue
            record = E.HoldingsRecord(
                E.NotificationType('00'),
                E.ResourceVersion(
                    E.ResourceVersionIdentifier(
                        E.ResourceVersionIDType('07'),
                        E.IDValue(journal['issn'])
                    ),
                    E.Title(
                        E.TitleType('01'),
                        E.TitleText(journal['title'])
                    ),
                    E.Publisher(
                        E.PublishingRole('01'),
                        E.PublisherName(journal['publisher_name'])
                    ),
                    self.addAllDeposits(journal, deposits)
                )
            )
            holdingsList.append(record)

    def execute(self, args):
        onix, holdingsList = self.skeleton()
        self.addJournals(holdingsList)
        self.output(0, et.tostring(onix, pretty_print=True, encoding="UTF-8"))

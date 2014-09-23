"""
Script to generate ONIX-PH describing content preserved in the PKP PLN.

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import os
import MySQLdb
import MySQLdb.cursors
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import ConfigParser
from datetime import datetime

# import staging_server_common

config = ConfigParser.ConfigParser()
config.read('../config_dev.cfg')

et.register_namespace('oph', 'http://www.editeur.org/onix/serials/SOH')

onix = Element('{http://www.editeur.org/onix/serials/SOH}ONIXPreservationHoldings')
onix.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
onix.set('xsi:schemaLocation', 'http://www.editeur.org/onix/serials/SOH ONIX_PreservationHoldings_V0.2.xsd')
onix.set('version', '0.2')

header = SubElement(onix, '{http://www.editeur.org/onix/serials/SOH}Header')
sender = SubElement(header, '{http://www.editeur.org/onix/serials/SOH}Sender')
senderName = SubElement(sender, '{http://www.editeur.org/onix/serials/SOH}SenderName')
senderName.text = "Public Knowlege Project PLN"

utc_datetime = datetime.utcnow()
senderDateTimeString = utc_datetime.strftime("%Y%m%dT%H%M%SZ")
senderDateTime = SubElement(header, '{http://www.editeur.org/onix/serials/SOH}SenderDateTime')
senderDateTime.text = senderDateTimeString

holdingsList = SubElement(onix, '{http://www.editeur.org/onix/serials/SOH}HoldingsList')
preservationAgency = SubElement(holdingsList, '{http://www.editeur.org/onix/serials/SOH}PreservationAgency')
preservationAgencyName = SubElement(preservationAgency, '{http://www.editeur.org/onix/serials/SOH}PreservationAgencyName')
preservationAgencyName.text = "Public Knowlege Project PLN"


# Some fake deposits for development.
deposits = [{'id': 1, 'deposit_volume': '4', 'deposit_pubdate': '2012-04-09'},
    {'id': 2, 'deposit_volume': '2', 'deposit_pubdate': '2014-01-01'}]

for deposit in deposits:
    holdingsRecord = SubElement(holdingsList, '{http://www.editeur.org/onix/serials/SOH}HoldingsRecord')
    # oph:NotificationType
    # oph:ResourceVersion
        # oph:ResourceVersionIdentifier
            # oph:ResourceVersionIDType
            # oph:IDValue
        # oph:Title
            # oph:TitleType
            # oph:TitleText
        # oph:Publisher
            # oph:PublishingRole
            # oph:PublisherName
        # oph:OnlinePackage
            # oph:PackageDetail
                # oph:Coverage
                    # oph:CoverageDescriptionLevel
                    # oph:SupplementInclusion
                    # oph:IndexInclusion
                    # oph:FixedCoverage [If we can use a single FixedCoverage as per
                    # http://www.editeur.org/files/ONIX%20for%20Serials%20-%20Coverage/20120326_ONIX_Coverage_overview_v1_0.pdf,
                    # that would be awesome.]
                        # oph:Sequence
                            # oph:SequenceStart
                                # oph:Enumeration
                                    # oph:Level1
                                        # oph:Unit
                                        # oph:Number
                                # oph:NominalDate
                                    # oph:Calendar
                                    # oph:DateFormat
                                    # oph:Date
                            # oph:SequenceEnd
                                # [same children as oph:SequenceStart]
                # oph:PreservationStatus
                    # oph:PreservationStatusCode
                    # oph:DateOfStatus
                # oph:VerificationStatus

tree = et.ElementTree(onix)
tree.write("pkppln_onixph.xml", xml_declaration=True, encoding='utf-8', method="xml")

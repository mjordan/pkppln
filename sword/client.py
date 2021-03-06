import os
import requests
from xml.etree import ElementTree as ET
import pkppln
from datetime import datetime


class SwordClient(object):

    """Very simple and special purpose SWORD client for the PLN to make
    deposits to LOCKSSOMatic an check on their status."""

    def __init__(self, sd_iri, journal_url, provider_uuid):
        """Initialize the client with the service document IRI and a
        content provider UUID."""
        self.sd_iri = sd_iri
        self.col_iri = None
        self.journal_url = journal_url
        self.provider_uuid = provider_uuid
        self.checksum_type = None
        self.max_upload_size = None

    def service_document(self):
        """Fetch a service document and parse it for more information."""
        headers = {
            'On-Behalf-Of': self.provider_uuid
        }
        if self.journal_url is not None:
            headers['Journal-Url'] = self.journal_url

        response = requests.get(self.sd_iri, headers=headers)
        if response.status_code != 200:
            raise Exception(
                ' - '.join([str(response.status_code), response.reason,
                            response.content])
            )

        # check response code here.
        try:
            root = ET.fromstring(response.content)
        except:
            raise

        collection = root.find(
            './/app:collection',
            namespaces=pkppln.namespaces
        )
        self.col_iri = collection.attrib['href']

        checksum_type = root.find(
            './/pkp:uploadChecksumType',
            namespaces=pkppln.namespaces
        )
        self.checksum_type = checksum_type.text

        max_upload_size = root.find(
            './/sword:maxUploadSize',
            namespaces=pkppln.namespaces
        )
        self.max_upload_size = max_upload_size.text
        return root

    def _checksum(self, filepath):
        """Calculate a checksum for a deposit."""
        if self.checksum_type == 'md5':
            return pkppln.file_md5(filepath)
        if self.checksum_type == 'sha1':
            return pkppln.file_sha1(filepath)
        raise Exception('Unknown checksum type: ' + self.checksum_type)

    def create_deposit(self, url, filepath, deposit, journal):
        """
        Send a deposit to the sword server. The deposit is staged at url for
        the server to download, and on the local file system at filepath.

        Throws an exception if the deposit failed.

        Returns the location header and response content as a tuple.
        """

        if self.col_iri is None:
            self.service_document()

        checksum_value = self._checksum(filepath)
        filesize = os.path.getsize(filepath)

        entry = ET.Element('entry', {
            'xmlns': pkppln.namespaces['entry'],
            'xmlns:lom': pkppln.namespaces['lom']
        })

        title = ET.SubElement(entry, 'title')
        title.text = 'Deposit to LOCKSSOMatic from PKPPLN.'
        id_element = ET.SubElement(entry, 'id')
        id_element.text = 'urn:uuid:' + deposit['deposit_uuid']

        updated = ET.SubElement(entry, 'updated')
        updated.text = str(datetime.now())

        author = ET.SubElement(entry, 'author')
        name = ET.SubElement(author, 'name')
        name.text = journal['title']

        summary = ET.SubElement(entry, 'summary', {'type': 'text'})
        summary.text = 'Deposit to LOCKSSOMatic from the PKP staging server.'

        content = ET.SubElement(entry, 'lom:content', {
            'size': str(filesize / 1000),
            'checksumType': self.checksum_type,
            'checksumValue': checksum_value,
        })
        content.text = url

        response = requests.post(self.col_iri,
                                 data=ET.tostring(entry, 'utf8'),
                                 headers={
                                     'Content-type': 'text/xml; charset=UTF-8'
                                 })
        if response.status_code != 201:
            raise Exception(str(response.status_code) +
                            ' ' + response.reason + '\n' + response.content)

        return response.headers['location'], response.content

    def modify_deposit(self, url, deposit):
        """We do not modify deposits. Only create new ones."""
        pass

    def statement(self, deposit):
        """Get the sword statement for a deposit, check on its status."""
        receipt = requests.get(deposit['deposit_receipt'])
        if receipt.status_code != 200:
            raise Exception(str(receipt.status_code) +
                            ' ' + receipt.reason + '\n' +
                            'Cannot find deposit receipt.')
        root = ET.fromstring(receipt.content)
        link = root.find(
            './/entry:link[@rel="http://purl.org/net/sword/terms/statement"]',
            pkppln.namespaces
        )
        if link is None:
            raise Exception('Cannot find statment link in deposit receipt.')

        statement = requests.get(link.attrib['href'])
        if statement.status_code != 200:
            raise Exception(str(statement.status_code) +
                            ' ' + statement.reason + '\n' +
                            'Cannot find statement.')

        return statement.content

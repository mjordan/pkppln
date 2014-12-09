import os
import requests
from xml.etree import ElementTree as ET
import pkppln
from datetime import datetime


class SwordClient(object):

    sd_iri = None

    col_iri = None

    checksum_type = None

    max_upload_size = None

    def __init__(self, sd_iri, provider_uuid):
        self.sd_iri = sd_iri
        self.provider_uuid = provider_uuid

    def service_document(self):
        headers = {
            'X-On-Behalf-Of': self.provider_uuid
        }
        response = requests.get(self.sd_iri, headers=headers)
        if response.status_code != 200:
            raise Exception(str(response.status_code) + ' ' + response.reason)
        
        # check response code here.
        root = ET.fromstring(response.content)
        collection = root.find(
            './/app:collection',
            namespaces=pkppln.namespaces
        )
        self.col_iri = collection.attrib['href']

        checksum_type = root.find(
            './/lom:uploadChecksumType',
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
        if self.checksum_type == 'md5':
            return pkppln.file_md5(filepath)
        if self.checksum_type == 'sha1':
            return pkppln.file_sha1(filepath)
        raise Exception('Unknown checksum type: ' + self.checksum_type)

    def create_deposit(self, url, filepath, deposit, journal):
        """
        Send a deposit to the sword server. The deposit is staged at url for the
        server to download, and on the local file system at filepath.
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
            'size': str(filesize),
            'checksumType': self.checksum_type,
            'checksumValue': checksum_value,
        })
        content.text = url

        return ET.dump(entry)
        # create a deposit document.
        # post the document
        # return the response
        pass

    def modify_deposit(self, url, deposit):
        pass

    def statement(self, deposit):
        pass

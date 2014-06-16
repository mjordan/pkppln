<?php

/**
 * @file plugins/generic/pln/classes/Deposit.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class Deposit
 * @ingroup plugins_generic_pln
 *
 * @brief Packages deposit objects for submission to a PLN
 */

import('classes.file.PublicFileManager');

class Deposit extends DataObject {
	
	/** @var string Atom entry filename */
	var $_atomEntryFileName = 'atom.xml';
	
	/** @var string deposit package filename */
	var $_packageFileName = 'package.zip';

	function DepositObject() {
		parent::DataObject();

		//Set up new deposits with a UUID
		$this->setUUID($this->_newUUID());
	}

	/**
	 * Get all deposit objects of this deposit.
	 * @return array of DepositObject
	 */
	function &getDepositObjects() {
		$depositObjectDao =& DAORegistry::getDAO('DepositObjectDAO');
		return $depositObjectDao->getByDepositId($this->getId());
	}

	function createAtom($journalId) {
		
		$depositObjects = $this->getDepositObjects();
		
		$destDir = $this->getPackagePath();
		if (is_dir($destDir) !== TRUE) { mkdir($destDir); }
		
		$atomFile = $destDir . DIRECTORY_SEPARATOR . $this->_atomEntryFileName;
		
		$atom  = new DOMDocument('1.0', 'utf-8');
		
		$entry = $atom->createElementNS('http://www.w3.org/2005/Atom', 'entry');
		$entry->setAttributeNS('http://www.w3.org/2000/xmlns/' ,'xmlns:dcterms', 'http://purl.org/dc/terms/');
		$entry->setAttributeNS('http://www.w3.org/2000/xmlns/' ,'xmlns:pkp', 'http://pkp.sfu.ca/SWORD');
		
		$email = $atom->createElement('email', 'email');
		$entry->appendChild($email);
		
		$title = $atom->createElement('title', 'title');
		$entry->appendChild($title);
		
		$pkp_issn = $atom->createElementNS('http://pkp.sfu.ca/SWORD', 'pkp:issn', 'issn');
		$entry->appendChild($pkp_issn);
		
		$id = $atom->createElement('id', 'urn:uuid:' . $this->getUUID());
		$entry->appendChild($id);
		
		$atom->appendChild($entry);
		
		
		
		
	}
	
	/**
	 * Create a zip archive of 
	 * @return string The full path of the created zip archive
	 */
	function createZip() {
		
		$depositObjects = $this->getDepositObjects();
		
		$destDir = $this->getPackagePath();
		if (is_dir($destDir) !== TRUE) { mkdir($destDir); }
		
		$packageFile = $destDir . DIRECTORY_SEPARATOR . $this->_packageFileName;
		$package = new ZipArchive();
		$package->open($packageFile, ZIPARCHIVE::CREATE | ZIPARCHIVE::OVERWRITE);
		
		foreach ($depositObjects as $depositObject) {
			$depositObjectFile =  $destDir . DIRECTORY_SEPARATOR . $depositObject->getContentType() . $depositObject->getContentId() . '.xml';
			if ($depositObject->exportDepositObjectToFile($depositObjectFile) !== FALSE) {
				$package->addFile($depositObjectFile, basename($depositObjectFile));
				unlink($depositObjectFile);
			}
		}
		
		$package->close();
		
		return $packageFile;
	}
	
	/**
	* Get/Set deposit uuid
	*/
	function getUUID() {
		return $this->getData('uuid');
	}
	function setUUID($uuid) {
		$this->setData('uuid', $uuid);
	}

	/**
	* Get/Set package path
	*/
	function getPackagePath() {
		return $this->getData('bag');
	}
	function setPackagePath($packagePath) {
		$this->setData('package_path', $packagePath);
	}

	/**
	* Get/Set deposit status
	*/
	function getStatus() {
		return $this->getData('status');
	}
	function setStatus($status) {
		$this->setData('status', $status);
	}

	/**
	* Get/Set last status check date
	*/
	function getLastStatusDate() {
		return $this->getData('date_status');
	}
	function setLastStatusDate($date_last_status) {
		$this->setData('date_status', $date_last_status);
	}

	/**
	* Get/Set deposit creation date
	*/
	function getDateCreated() {
		return $this->getData('date_created');
	}
	function setDateCreated($dateCreated) {
		$this->setData('date_created', $dateCreated);
	}

	/**
	* Get/Set deposit modification date
	*/
	function getDateModified() {
		return $this->getData('date_modified');
	}
	function setDateModified($dateModified) {
		$this->setData('date_modified', $dateModified);
	}

	/**
	 * Create a new UUID
	 * /
	function _newUUID() {
		mt_srand((double)microtime()*10000);
		$charid = strtoupper(md5(uniqid(rand(), true)));
		$hyphen = '-';
		$uuid = substr($charid, 0, 8).$hyphen
				.substr($charid, 8, 4).$hyphen
				.substr($charid,12, 4).$hyphen
				.substr($charid,16, 4).$hyphen
				.substr($charid,20,12);
        return $uuid;
	}
}

?>

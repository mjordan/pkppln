<?php

/**
 * @file plugins/generic/pln/classes/DepositPackager.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v2. For full terms see the file docs/COPYING.
 *
 * @class DepositPackager
 * @ingroup plugins_generic_pln
 *
 * @brief Packages deposit object(s) for deposit in a PLN
 */

 

 
 
import('classes.file.PublicFileManager');

require_once('lib/pkp/lib/swordappv2/packager_atom_twostep.php');

class DepositPackager extends PackagerAtomTwoStep {
	
	/** @var string output path for packager files */
	var $_outPath;
	
	/** @var string file directory for packager files */
	var $_fileDir;
	
	/** @var array of deposit objects to be deposited */
	var $_depositObjects = array();
	
	/** @var string Atom entry filename */
	var $_atomEntryFileName = 'atom.xml';
	
	/** @var string deposit package filename */
	var $_packageFileName = 'package.zip';
	
	/** @var string packaging */
	var $_packaging = 'http://purl.org/net/sword/package/SimpleZip';
	
	/** @var string package content type */
	var $_contentType = 'application/zip';

	/**
	 * Constructor.
	 */
	function DepositPackager(&$deposit) {

		$fileManager = new PublicFileManager();

		// Create temporary directory for Atom entry & deposit files
		$this->_outPath = $fileManager->getJournalFilesPath($journalId) . DIRECTORY_SEPARATOR . 'deposits' . DIRECTORY_SEPARATOR . $deposit->getUUID();
		unlink($this->_outPath);
		mkdir($this->_outPath);
		mkdir($this->_outPath . DIRECTORY_SEPARATOR . $this->_fileDir);
		$_depositObjects = $deposit->getDepositObjects();
		
		parent::__construct($this->_outPath, $this->_fileDir, $this->_outPath, '');
	}

	/**
	 * Add an individual deposit object to the package
	 */
	function addDepositObject(&$depositObject) {
		$this->_depositObjects[] = $depositObject;
	}

	/**
	 * Set the deposit objects for the package
	 */
	function setDepositObjects(&$depositObjects) {
		$this->_depositObjects = $depositObjects;
	}
	
	/**
	 * Create Atom entry. Wrapper renames parent::create() to distinguish between
	 * Atom entry creation and deposit package creation.
	 */
	function createAtomEntry() {
		$this->create();
	}
	
	/**
	 * Create deposit package of files.
	 */
	function createPackage() {
		
	}

	/**
	 * Get path to Atom entry file.
	 * @return string
	 */
	function getAtomEntryFilePath() {
		return $this->_outPath .'/'. $this->_fileDir .'/'. $this->_atomEntryFileName;
	}	 

	/**
	 * Get path to deposit package.
	 * @return string
	 */
	function getPackageFilePath() {
		return $this->_outPath .'/'. $this->_fileDir .'/'. $this->_packageFileName;		 
	}	 
	
	/**
	 * Get packaging format of deposit.
	 * @return string
	 */
	function getPackaging() {
		return $this->_packaging;
	}
	
	/**
	 * Get content type of deposit.
	 * @return string
	 */
	function getContentType() {
		return $this->_contentType;
	}
		
}

?>
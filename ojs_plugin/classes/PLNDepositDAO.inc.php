<?php

/**
 * @file plugins/generic/pln/PLNDepositDAO.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class PLNDepositDAO
 * @ingroup plugins_generic_pln
 *
 * @brief Operations for adding a PLN deposit
 */

import('lib.pkp.classes.db.DAO');

class PLNDepositDAO extends DAO {
  
	/** @var $_parentPluginName string Name of parent plugin */
	var $_parentPluginName;

	/**
	 * Constructor
	 */
	function PLNDepositDAO($parentPluginName) {
		$this->_parentPluginName = $parentPluginName;
		parent::DAO();
	}

	/**
	 * Insert a new PLN deposit
	 * @param $plnDeposit PLNDeposit
	 * @return int inserted PLNDeposit id
	 */
	function insertPLNDeposit(&$plnDeposit) {
		$this->update(
			'INSERT INTO pln_deposits
				(issue_id, , study_id, content_source_uri)
				VALUES
				(?, ?, ?, ?)',
			array(
				$plnDeposit->getSuppFileId(),
				$plnDeposit->getSubmissionId(),
				// Some parent data may not exist when record is inserted, set it here
				$dvFile->getStudyId() ? $dvFile->getStudyId() : 0,
				$dvFile->getContentSourceUri() ? $dvFile->getContentSourceUri() : ''
			)
		);
		$dvFile->setId($this->getInsertPLNDepositId());
		return $dvFile->getId();
	}

  /**
   * Update PLN deposit
   * @param $plnDeposit PLNDeposit
   * @return int PLNDeposit id
   */
	function updatePLNDeposit(&$plnDeposit) {
		$returner = $this->update(
			'UPDATE dataverse_files
				SET
				supp_id = ?,
				study_id = ?,
				submission_id = ?,
				content_source_uri = ?
				WHERE dvfile_id = ?',
			array(
				$dvFile->getSuppFileId(),
				$dvFile->getStudyId(),
				$dvFile->getSubmissionId(),
				$dvFile->getContentSourceUri(),
				$dvFile->getId()
			)
		);
		return $returner;
	}  
  
	/**
	 * Get the ID of the last inserted PLN file.
	 * @return int
	 */
	function getInsertPLNDepositId() {
		return $this->getInsertId('dataverse_files', 'dvfile_id');
	}  
  
  
	/**
	 * Delete a PLNDeposit
	 * @param $dvFile PLNDeposit
	 */
	function deletePLNDeposit(&$dvFile) {
		return $this->deletePLNDepositById($dvFile->getId());
	}

	/**
	 * Delete a PLN file by ID.
	 * @param $dvFileId int
	 * @param $submissionId int optional
	 */
	function deletePLNDepositById($dvFileId, $submissionId = null) {
		if (isset($submissionId)) {
			$returner = $this->update('DELETE FROM dataverse_files WHERE dvfile_id = ? AND submission_id = ?', array($dvFileId, $submissionId));
			return $returner;
		}
		return $this->update('DELETE FROM dataverse_files WHERE dvfile_id = ?', $dvFileId);
	}
  
	/**
	 * Delete PLN files associated with a study
	 * @param $studyId int
	 */
	function deletePLNDepositsByStudyId($studyId) {
		$dvFiles =& $this->getPLNDepositsByStudyId($studyId);
		foreach ($dvFiles as $dvFile) {
			$this->deletePLNDeposit($dvFile);
		}
	}
  
  
  /**
   * Retrieve PLN file by supp id & optional submission 
   * @param int $suppFileId
   * @param int $submissionId
   * @return PLNDeposit
   */
  function &getPLNDepositBySuppFileId($suppFileId, $submissionId = null) {
		$params = array($suppFileId);
		if ($submissionId) $params[] = $submissionId;

    $result =& $this->retrieve(
			'SELECT * FROM dataverse_files WHERE supp_id = ?' . ($submissionId?' AND submission_id = ?':''),
			$params
		);

		$returner = null;
		if ($result->RecordCount() != 0) {
			$returner =& $this->_returnPLNDepositFromRow($result->GetRowAssoc(false));
		}

		$result->Close();
		unset($result);

		return $returner;    
  }
  
	/**
	 * Retrieve PLN files for a submission
	 * @param $submissionId int
	 * @return array PLNDeposits
	 */
	function &getPLNDepositsBySubmissionId($submissionId) {
		$dvFiles = array();

		$result =& $this->retrieve(
			'SELECT * FROM dataverse_files WHERE submission_id = ?',
			(int) $submissionId
		);

		while (!$result->EOF) {
			$dvFiles[] =& $this->_returnPLNDepositFromRow($result->GetRowAssoc(false));
			$result->moveNext();
		}

		$result->Close();
		unset($result);

		return $dvFiles;
	}  
  
	/**
	 * Retrieve PLN files for a study
	 * @param $submissionId int
	 * @return array PLNDeposits
	 */
	function &getPLNDepositsByStudyId($studyId) {
		$dvFiles = array();

		$result =& $this->retrieve(
			'SELECT * FROM dataverse_files WHERE study_id = ?',
			(int) $studyId
		);

		while (!$result->EOF) {
			$dvFiles[] =& $this->_returnPLNDepositFromRow($result->GetRowAssoc(false));
			$result->moveNext();
		}

		$result->Close();
		unset($result);

		return $dvFiles;
	}    
  
	/**
	 * Internal function to return PLNDeposit object from a row.
	 * @param $row array
	 * @return PLNDeposit
	 */
	function &_returnPLNDepositFromRow(&$row) {
		$dataversePlugin =& PluginRegistry::getPlugin('generic', $this->_parentPluginName);
		$dataversePlugin->import('classes.PLNDeposit');
		$dvFile = new PLNDeposit();
		$dvFile->setId($row['dvfile_id']);    
		$dvFile->setSuppFileId($row['supp_id']);        
		$dvFile->setStudyId($row['study_id']);
		$dvFile->setSubmissionId($row['submission_id']);
		$dvFile->setContentSourceUri($row['content_source_uri']);
		return $dvFile;
	}    
  
  /**
	 * Update the PLN deposit status of a supplementary file.
   * Files with deposit status = true will be deposited/updated in PLN.
	 * @param $suppFileId int
	 * @param $depositStatus bool
	 */
	function setDepositStatus($suppFileId, $depositStatus) {
		$idFields = array(
			'supp_id', 'locale', 'setting_name'
		);
		$updateArray = array(
			'supp_id' => $suppFileId,
			'locale' => '',
			'setting_name' => 'dataverseDeposit',
			'setting_type' => 'bool',
			'setting_value' => (bool)$depositStatus
		);
		$this->replace('article_supp_file_settings', $updateArray, $idFields);
	}  

  function setContentSourceUri($suppFileId, $contentSourceUri) {
		$idFields = array(
			'supp_id', 'locale', 'setting_name'
		);
		$updateArray = array(
			'supp_id' => $suppFileId,
			'locale' => '',
			'setting_name' => 'dataverseContentSourceUri',
			'setting_type' => 'string',
			'setting_value' => $contentSourceUri
		);
		$this->replace('article_supp_file_settings', $updateArray, $idFields);
    
  }
}
?>

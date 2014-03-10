<?php

/**
 * @file plugins/generic/lockssomatic/LOMPayloadDAO.inc.php
 *
 * Copyright (c) 2003-2013 John Willinsky
 * Distributed under the GNU GPL v2. For full terms see the file docs/COPYING.
 *
 * @class LOMPayloadDAO
 * @ingroup plugins_generic_lockssomatic
 *
 * @brief Operations for adding a Lockss-O-Matic payload
 */

import('lib.pkp.classes.db.DAO');

class LOMPayloadDAO extends DAO {
  
	/** @var $_parentPluginName string Name of parent plugin */
	var $_parentPluginName;

	/**
	 * Constructor
	 */
	function LOMPayloadDAO($parentPluginName) {
		$this->_parentPluginName = $parentPluginName;
		parent::DAO();
	}
  
	/**
	 * Insert a new LOM paylaod 
	 * @param $lomPayload LOMPayload
   * @return int inserted LOMPayload id
	 */
	function insertLOMPayload(&$lomPayload) {
		$this->update(
			'INSERT INTO lom_payloads
				(issue_id, , study_id, content_source_uri)
				VALUES
				(?, ?, ?, ?)',
			array(
				$dvFile->getSuppFileId(),
				$dvFile->getSubmissionId(),
        // Parent study and Dataverse Uri may not exist when record is inserted          
        $dvFile->getStudyId() ? $dvFile->getStudyId() : 0,
        $dvFile->getContentSourceUri() ? $dvFile->getContentSourceUri() : ''
			)
		);
		$dvFile->setId($this->getInsertLOMPayloadId());
		return $dvFile->getId();
	}
  
  /**
   * Update Dataverse File
   * @param DatverseFile $dvFile
   * @return int LOMPayload id
   */
	function updateLOMPayload(&$dvFile) {
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
	 * Get the ID of the last inserted Dataverse file.
	 * @return int
	 */
	function getInsertLOMPayloadId() {
		return $this->getInsertId('dataverse_files', 'dvfile_id');
	}  
  
  
	/**
	 * Delete a LOMPayload
	 * @param $dvFile LOMPayload
	 */
	function deleteLOMPayload(&$dvFile) {
		return $this->deleteLOMPayloadById($dvFile->getId());
	}

	/**
	 * Delete a Dataverse file by ID.
	 * @param $dvFileId int
	 * @param $submissionId int optional
	 */
	function deleteLOMPayloadById($dvFileId, $submissionId = null) {
		if (isset($submissionId)) {
			$returner = $this->update('DELETE FROM dataverse_files WHERE dvfile_id = ? AND submission_id = ?', array($dvFileId, $submissionId));
			return $returner;
		}
		return $this->update('DELETE FROM dataverse_files WHERE dvfile_id = ?', $dvFileId);
	}
  
	/**
	 * Delete Dataverse files associated with a study
	 * @param $studyId int
	 */
	function deleteLOMPayloadsByStudyId($studyId) {
		$dvFiles =& $this->getLOMPayloadsByStudyId($studyId);
		foreach ($dvFiles as $dvFile) {
			$this->deleteLOMPayload($dvFile);
		}
	}
  
  
  /**
   * Retrieve Dataverse file by supp id & optional submission 
   * @param int $suppFileId
   * @param int $submissionId
   * @return LOMPayload
   */
  function &getLOMPayloadBySuppFileId($suppFileId, $submissionId = null) {
		$params = array($suppFileId);
		if ($submissionId) $params[] = $submissionId;

    $result =& $this->retrieve(
			'SELECT * FROM dataverse_files WHERE supp_id = ?' . ($submissionId?' AND submission_id = ?':''),
			$params
		);

		$returner = null;
		if ($result->RecordCount() != 0) {
			$returner =& $this->_returnLOMPayloadFromRow($result->GetRowAssoc(false));
		}

		$result->Close();
		unset($result);

		return $returner;    
  }
  
	/**
	 * Retrieve Dataverse files for a submission
	 * @param $submissionId int
	 * @return array LOMPayloads
	 */
	function &getLOMPayloadsBySubmissionId($submissionId) {
		$dvFiles = array();

		$result =& $this->retrieve(
			'SELECT * FROM dataverse_files WHERE submission_id = ?',
			(int) $submissionId
		);

		while (!$result->EOF) {
			$dvFiles[] =& $this->_returnLOMPayloadFromRow($result->GetRowAssoc(false));
			$result->moveNext();
		}

		$result->Close();
		unset($result);

		return $dvFiles;
	}  
  
	/**
	 * Retrieve Dataverse files for a study
	 * @param $submissionId int
	 * @return array LOMPayloads
	 */
	function &getLOMPayloadsByStudyId($studyId) {
		$dvFiles = array();

		$result =& $this->retrieve(
			'SELECT * FROM dataverse_files WHERE study_id = ?',
			(int) $studyId
		);

		while (!$result->EOF) {
			$dvFiles[] =& $this->_returnLOMPayloadFromRow($result->GetRowAssoc(false));
			$result->moveNext();
		}

		$result->Close();
		unset($result);

		return $dvFiles;
	}    
  
	/**
	 * Internal function to return LOMPayload object from a row.
	 * @param $row array
	 * @return LOMPayload
	 */
	function &_returnLOMPayloadFromRow(&$row) {
		$dataversePlugin =& PluginRegistry::getPlugin('generic', $this->_parentPluginName);
		$dataversePlugin->import('classes.LOMPayload');
		$dvFile = new LOMPayload();
		$dvFile->setId($row['dvfile_id']);    
		$dvFile->setSuppFileId($row['supp_id']);        
		$dvFile->setStudyId($row['study_id']);
		$dvFile->setSubmissionId($row['submission_id']);
		$dvFile->setContentSourceUri($row['content_source_uri']);
		return $dvFile;
	}    
  
  /**
	 * Update the Dataverse deposit status of a supplementary file.
   * Files with deposit status = true will be deposited/updated in Dataverse.
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

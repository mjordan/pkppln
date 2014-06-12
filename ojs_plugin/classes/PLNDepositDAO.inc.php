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

import('classes.article.Article');
import('classes.issue.Issue');

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
	 * Retrieve a deposit by deposit ID.
	 * @param $depositId int
	 * @return PLNDeposit
	 */
	function &getDeposit($depositId) {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposits WHERE deposit = ?', $depositId
		);

		$returner = null;
		if ($result->RecordCount() != 0) {
			$returner =& $this->_returnDepositFromRow($result->GetRowAssoc(false));
		}
		$result->Close();
		return $returner;
	}

	/**
	 * Insert deposit
	 * @param $plnDeposit PLNDeposit
	 * @return int inserted PLNDeposit id
	 */
	function insertDeposit(&$plnDeposit) {
		$ret = $this->update(
			sprintf('
				INSERT INTO pln_deposits
					(uuid,
					journal_id,
					content_type,
					content_id,
					date_created,
					date_modified,
					bag_path,
					bag_checksum,
					bag_size,
					date_status,
					status)
				VALUES
					(?, ?, ?, ?, %s, %s, ?, ?, ?, %s, ?)',
				$this->datetimeToDB($plnDeposit->getDateCreated()),
				$this->datetimeToDB($plnDeposit->getDateModified()),
				$this->datetimeToDB($plnDeposit->getLastStatusDate()))
			),
			array(
				$plnDeposit->getUUID(),
				$plnDeposit->getJournalId(),
				$plnDeposit->getContentType(),
				$plnDeposit->getContentId(),
				$plnDeposit->getBagPath(),
				$plnDeposit->getBagChecksum(),
				$plnDeposit->getBagSize(),
				$plnDeposit->getStatus()
			)
		);
		$plnDeposit->setId($this->getInsertDepositId());
		return $plnDeposit->getId();
	}

  /**
   * Update deposit
   * @param $plnDeposit PLNDeposit
   * @return int updated PLNDeposit id
   */
	function updateDeposit(&$plnDeposit) {
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
	 * Get the ID of the last inserted deposit.
	 * @return int
	 */
	function getInsertDepositId() {
		return $this->getInsertId('pln_deposits', 'deposit_id');
	}
  
	/**
	 * Internal function to return a deposit object from a row.
	 * @param $row array
	 * @return PLNDeposit
	 */
	function &_returnDepositFromRow(&$row) {
		$plnPlugin =& PluginRegistry::getPlugin('generic', $this->parentPluginName);
		$plnPlugin->import('classes.PLNDeposit');

		$deposit = new PLNDeposit();
		$deposit->setId($row['deposit_id']);
		$deposit->setJournalId($row['journal_id']);
		$deposit->setStatus($row['status']);
		$deposit->setUserId($row['user_id']);
		$deposit->setEditorId($row['editor_id']);
		$deposit->setAuthorType($row['author_type']);
		$deposit->setPublisher($row['publisher']);
		$deposit->setUrl($row['url']);
		$deposit->setYear($row['year']);
		$deposit->setLanguage($row['language']);
		$deposit->setCopy($row['copy']);
		$deposit->setEdition($row['edition']);
		$deposit->setPages($row['pages']);
		$deposit->setISBN($row['isbn']);
		$deposit->setArticleId($row['article_id']);
		$deposit->setNotes($row['notes']);
		$deposit->setDateCreated($row['date_created']);
		$deposit->setDateRequested($row['date_requested']);
		$deposit->setDateAssigned($row['date_assigned']);
		$deposit->setDateMailed($row['date_mailed']);
		$deposit->setDateDue($row['date_due']);
		$deposit->setDateSubmitted($row['date_submitted']);

		$this->getDataObjectSettings('books_for_review_settings', 'book_id', $row['book_id'], $book);

		HookRegistry::call('PLNDepositDAO::_returnDepositFromRow', array(&$deposit, &$row));

		return $book;
	}
}
?>

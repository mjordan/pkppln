<?php

/**
 * @file plugins/generic/pln/DepositObjectDAO.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class DepositObjectDAO
 * @ingroup plugins_generic_pln
 *
 * @brief Operations for adding a PLN deposit object
 */

import('classes.article.Article');
import('classes.issue.Issue');

class DepositObjectDAO extends DAO {
  
	/** @var $_parentPluginName string Name of parent plugin */
	var $_parentPluginName;

	/**
	 * Constructor
	 */
	function DepositObjectDAO($parentPluginName) {
		parent::DAO();
		$this->_parentPluginName = $parentPluginName;
	}

	/**
	 * Retrieve a deposit object by deposit object id.
	 * @param $depositId int
	 * @return DepositObject
	 */
	function &getById($depositObjectId) {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposit_objects WHERE deposit_object_id = ?', (int) $depositObjectId
		);

		$returner = null;
		if ($result->RecordCount() != 0) {
			$returner =& $this->_returnDepositObjectFromRow($result->GetRowAssoc(false));
		}
		$result->Close();
		return $returner;
	}

	/**
	 * Retrieve all deposit objects by deposit id.
	 * @param $depositId int
	 * @return array DepositObject ordered by sequence
	 */
	function &getByDepositId($depositId) {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposit_objects WHERE deposit_id = ?', (int) $depositId
		);

		$returner = array();
		while (!$result->EOF) {
			$returner[] =& $this->_returnDepositObjectFromRow($result->GetRowAssoc(false));
			$result->MoveNext();
		}
		$result->Close();
		return $returner;
	}
	
	/**
	 * Retrieve all deposit objects that don't yet have a deposit id.
	 * @return array DepositObject ordered by sequence
	 */
	function &getNew() {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposit_objects WHERE deposit_id = null'
		);

		$returner = array();
		while (!$result->EOF) {
			$returner[] =& $this->_returnDepositObjectFromRow($result->GetRowAssoc(false));
			$result->MoveNext();
		}
		$result->Close();
		return $returner;
	}

	/**
	 * Insert deposit object
	 * @param $depositObject DepositObject
	 * @return int inserted DepositObject id
	 */
	function insertDepositObject(&$depositObject) {
		$ret = $this->update(
			sprintf('
				INSERT INTO pln_deposit_objects
					(journal_id,
					content_id,
					content_type,
					deposit_id,
					date_created,
					date_modified)
				VALUES
					(?, ?, ?, %s, %s)',
				$this->datetimeToDB(new DateTime()),
				$this->datetimeToDB($depositObject->getDateModified())
			),
			array(
				(int) $depositObject->getJournalId(),
				(int) $depositObject->getContentId(),
				(int) $depositObject->getContentType(),
				(int) $depositObject->getDepositId()
			)
		);
		$depositObject->setId($this->getInsertDepositObjectId());
		return $depositObject->getId();
	}

	/**
	 * Update deposit object
	 * @param $depositObject DepositObject
	 * @return int updated DepositObject id
	 */
	function updateDepositObject(&$depositObject) {
		$ret = $this->update(
			sprintf('
				UPDATE pln_deposit_objects SET
					journal_id = ?,
					content_type = ?,
					content_id = ?,
					deposit_id = ?,
					date_created = %s,
					date_modified = %s,
				WHERE deposit_object_id = ?',
				$this->datetimeToDB($depositObject->getDateCreated()),
				$this->datetimeToDB(new DateTime())
			),
			array(
				(int) $depositObject->getJournalId(),
				(int) $depositObject->getContentType(),
				(int) $depositObject->getContentId(),
				(int) $depositObject->getDepositId(),
				(int) $depositObject->getId()
			)
		);
		return $ret;
	}

	/**
	 * Get the ID of the last inserted deposit object.
	 * @return int
	 */
	function getInsertDepositObjectId() {
		return $this->getInsertId('pln_deposit_objects', 'deposit_object_id');
	}

	/**
	 * Construct a new data object corresponding to this DAO.
	 * @return DepositObject
	 */
	function newDataObject() {
		$plnPlugin =& PluginRegistry::getPlugin('generic', $this->parentPluginName);
		$plnPlugin->import('classes.DepositObject');
		return new DepositObject();
	}

	/**
	 * Internal function to return a deposit object from a row.
	 * @param $row array
	 * @return DepositObject
	 */
	function &_returnDepositObjectFromRow(&$row) {
		$depositObject = $this->newDataObject();
		$depositObject->setId($row['deposit_object_id']);
		$depositObject->setJournalId($row['journal_id']);
		$depositObject->setContentType($row['content_type']);
		$depositObject->setContentId($row['content_id']);
		$depositObject->setDepositId($row['deposit_id']);
		$depositObject->setDateCreated($row['date_created']);
		$depositObject->setDateModified($row['date_modified']);

		HookRegistry::call('DepositObjectDAO::_returnDepositObjectFromRow', array(&$depositObject, &$row));

		return $depositObject;
	}
}
?>

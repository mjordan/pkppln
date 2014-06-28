<?php

/**
 * @file plugins/generic/pln/DepositDAO.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class DepositDAO
 * @ingroup plugins_generic_pln
 *
 * @brief Operations for adding a PLN deposit
 */

class DepositDAO extends DAO {
  
	/** @var $_parentPluginName string Name of parent plugin */
	var $_parentPluginName;

	/**
	 * Constructor
	 */
	function DepositDAO($parentPluginName) {
		parent::DAO();
		$this->_parentPluginName = $parentPluginName;
	}

	/**
	 * Retrieve a deposit by deposit id.
	 * @param $depositId int
	 * @return Deposit
	 */
	function &getById($depositId) {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposits WHERE deposit_id = ?', (int) $depositId
		);

		$returner = null;
		if ($result->RecordCount() != 0) {
			$returner =& $this->_returnDepositFromRow($result->GetRowAssoc(false));
		}
		$result->Close();
		return $returner;
	}

	/**
	 * Retrieve all newly-created deposits (ones with no package path)
	 * @return array Deposit
	 */
	function &getNew() {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposits WHERE package_path = null'
		);

		$returner = array();
		while (!$result->EOF) {
			$returner[] =& $this->_returnDepositFromRow($result->GetRowAssoc(false));
			$result->MoveNext();
		}
		$result->Close();
		return $returner;
	}
	
	/**
	 * Retrieve all deposits that need packaging
	 * @return array Deposit
	 */
	function &getNeedPackaging() {
		$result =& $this->retrieve(
			'
			SELECT DISTINCT d.* FROM pln_deposits d LEFT JOIN pln_deposit_objects o ON
				(d.deposit_id = o.deposit_id)
			WHERE
				(d.date_modified != null and
				o.date_modified != null and
				o.date_modified > d.date_modified) or
				(d.status = ?)', (int) PLN_PLUGIN_DEPOSIT_STATUS_NONE
		);

		$returner = array();
		while (!$result->EOF) {
			$returner[] =& $this->_returnDepositFromRow($result->GetRowAssoc(false));
			$result->MoveNext();
		}
		$result->Close();
		
		return $returner;
		
	}
	
	/**
	 * Retrieve all deposits that need transferring
	 * @return array Deposit
	 */
	function &getNeedTransferring() {
		$result =& $this->retrieve(
			'SELECT * FROM pln_deposits WHERE status = ?', (int) PLN_PLUGIN_DEPOSIT_STATUS_PACKAGED
		);

		$returner = array();
		while (!$result->EOF) {
			$returner[] =& $this->_returnDepositFromRow($result->GetRowAssoc(false));
			$result->MoveNext();
		}
		$result->Close();
		
		return $returner;
		
	}
	
		/**
	 * Retrieve all deposits that need a status update
	 * @return array Deposit
	 */
	function &getNeedStatus() {
		$result =& $this->retrieve(
			'
			SELECT * FROM pln_deposits WHERE
			status = ? or
			status = ? or
			status = ? or
			',
			(int) PLN_PLUGIN_DEPOSIT_STATUS_TRANSFERRED,
			(int) PLN_PLUGIN_DEPOSIT_STATUS_RECEIVED,
			(int) PLN_PLUGIN_DEPOSIT_STATUS_SYNCING
		);

		$returner = array();
		while (!$result->EOF) {
			$returner[] =& $this->_returnDepositFromRow($result->GetRowAssoc(false));
			$result->MoveNext();
		}
		$result->Close();
		
		return $returner;
		
	}
	
	/**
	 * Insert deposit object
	 * @param $deposit Deposit
	 * @return int inserted Deposit id
	 */
	function insertDeposit(&$deposit) {
		$ret = $this->update(
			sprintf('
				INSERT INTO pln_deposits
					(journal_id,
					uuid,
					package_path,
					status,
					date_status,
					date_created,
					date_modified)
				VALUES
					(?, ?, %s, %s, %s)',
				$this->datetimeToDB($deposit->getLastStatusDate()),
				$this->datetimeToDB(new DateTime()),
				$this->datetimeToDB($deposit->getDateModified())
			),
			array(
				(int) $deposit->getJournalId(),
				(int) $deposit->getUUID(),
				(int) $deposit->getPackage(),
				(int) $deposit->getStatus()
			)
		);
		$deposit->setId($this->getInsertDepositId());
		return $deposit->getId();
	}

	/**
	 * Update deposit object
	 * @param $depositObject DepositObject
	 * @return int updated DepositObject id
	 */
	function updateDeposit(&$depositObject) {
		$ret = $this->update(
			sprintf('
				UPDATE pln_deposits SET
					journal_id = ?,
					uuid = ?,
					package_path = ?,
					status = ?,
					date_status = %s,
					date_created = %s,
					date_modified = %s,
				WHERE deposit_id = ?',
				$this->datetimeToDB($deposit->getLastStatusDate()),
				$this->datetimeToDB($deposit->getDateCreated()),
				$this->datetimeToDB(new DateTime())
			),
			array(
				(int) $deposit->getJournalId(),
				(int) $deposit->getUUID(),
				(int) $deposit->getPackagePath(),
				(int) $deposit->getStatus(),
				(int) $deposit->getId()
			)
		);
		return $ret;
	}

	/**
	 * Get the ID of the last inserted deposit.
	 * @return int
	 */
	function getInsertDepositId() {
		return $this->getInsertId('pln_deposits', 'deposit_id');
	}
  
	/**
	 * Construct a new data object corresponding to this DAO.
	 * @return Deposit
	 */
	function newDataObject() {
		$plnPlugin =& PluginRegistry::getPlugin('generic', $this->parentPluginName);
		$plnPlugin->import('classes.Deposit');
		return new Deposit();
	}

	/**
	 * Internal function to return a deposit from a row.
	 * @param $row array
	 * @return Deposit
	 */
	function &_returnDepositFromRow(&$row) {
		$deposit = $this->newDataObject();
		$deposit->setId($row['deposit_id']);
		$deposit->setJournalId($row['journal_id']);
		$deposit->setUUID($row['uuid']);
		$deposit->setPackagePath($row['package_path']);
		$deposit->setStatus($row['status']);
		$deposit->setLastStatusDate($row['date_status']);
		$deposit->setDateCreated($row['date_created']);
		$deposit->setDateModified($row['date_modified']);

		HookRegistry::call('DepositDAO::_returnDepositFromRow', array(&$deposit, &$row));

		return $deposit;
	}
}

?>

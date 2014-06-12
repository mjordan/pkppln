<?php

/**
 * @file plugins/generic/pln/classes/PLNDeposit.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class PLNDeposit
 * @ingroup plugins_generic_pln
 *
 * @brief Basic class describing a deposit stored in the PLN
 */
import('classes.article.Article');
import('classes.issue.Issue');

define('PLN_PLUGIN_DEPOSIT_CONTENT_ISSUE', get_class(new Article()));
define('PLN_PLUGIN_DEPOSIT_CONTENT_ARTICLE', get_class(new Issue()));

define('PLN_PLUGIN_HTTP_STATUS_OK', 200);

class PLNDeposit extends DataObject {

	function PLNDeposit() {
		parent::DataObject();
	}

	/**
	* Get/Set content helpers
	*/
	function getContent() {
		$content_type = $this->getData('content_type');
		$content_id = $this->getData('content_id');
		$content = null;

		switch ($content_type) {
			case PLN_PLUGIN_DEPOSIT_CONTENT_ISSUE:
				$issueDao =& DAORegistry::getDAO('IssueDAO');
				$content = $issueDao->getIssueById($content_id,$this->getJournalId());
			case PLN_PLUGIN_DEPOSIT_CONTENT_ARTICLE:
				$articleDao =& DAORegistry::getDAO('ArticleDAO');
				$content = $articleDao->getArticle($content_id,$this->getJournalId());
			default:
		}
		return $content;
	}
	function setContent(&$content) {
		
		switch (get_class($content)) {
			case PLN_PLUGIN_DEPOSIT_CONTENT_ISSUE:
			case PLN_PLUGIN_DEPOSIT_CONTENT_ARTICLE:
				$content_type = get_class($content);
				$content_id = $content->getId();
				$this->setData('content_id', $content_id);
				$this->setData('content_type', $content_type);
				break;
			default:
		}
		
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
	* Get/Set content type
	*/
	function getContentType() {
		return $this->getData('content_type');
	}
	function setContentType($content_type) {
		$this->setData('content_type', $content_type);
	}

	/**
	* Get/Set content id
	*/
	function getContentId() {
		return $this->getData('content_id');
	}
	function setContentId($content_id) {
		$this->setData('content_id', $content_id);
	}

	/**
	* Get/Set deposit journal id
	*/
	function getJournalId() {
		return $this->getData('journal_id');
	}
	function setJournalId($journalId) {
		$this->setData('journal_id', $journalId);
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
	* Get/Set bag path
	*/
	function getBagPath() {
		return $this->getData('bag_path');
	}
	function setBagPath($bagPath) {
		$this->setData('bag_path', $bagPath);
	}

	/**
	* Get/Set bag checksum
	*/
	function getBagChecksum() {
		return $this->getData('bag_checksum');
	}
	function setBagChecksum($bagChecksum) {
		$this->setData('bag_checksum', $bagChecksum);
	}

	/**
	* Get/Set bag size
	*/
	function getBagSize() {
		return $this->getData('bag_size');
	}
	function setBagSize($bagSize) {
		$this->setData('bag_size', $bagSize);
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
	* Get/Set deposit status
	*/
	function getStatus() {
		return $this->getData('status');
	}
	function setStatus($status) {
		$this->setData('status', $status);
	}

}

?>

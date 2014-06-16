<?php

/**
 * @file plugins/generic/pln/classes/DepositObject.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class DepositObject
 * @ingroup plugins_generic_pln
 *
 * @brief Basic class describing a deposit stored in the PLN
 */
import('classes.article.Article');
import('classes.issue.Issue');

define('PLN_PLUGIN_DEPOSIT_OBJECT_ISSUE', get_class(new Article()));
define('PLN_PLUGIN_DEPOSIT_OBJECT_ARTICLE', get_class(new Issue()));

class DepositObject extends DataObject {

	function DepositObject() {
		parent::DataObject();
	}

	/**
	* Export the deposit object using the OJS native XML format
	* @return string OJS Native XML for an article or an issue
	*/
	function exportDepositObjectToFile($fileName) {
		if ((is_writable($fileName)) && (($file = fopen($fileName,'w')) !== FALSE)) {
			$ret = fwrite($file, 'Some XML content.');
			if ($ret === FALSE) {
				return $ret;
			}
		}
	}

	/**
	* Get/Set content helpers
	*/
	function getContent() {
		$content_type = $this->getContentType();
		$content_id = $this->getContentId();
		$content = null;

		switch ($content_type) {
			case PLN_PLUGIN_DEPOSIT_OBJECT_ISSUE:
				$issueDao =& DAORegistry::getDAO('IssueDAO');
				$content = $issueDao->getIssueById($content_id,$this->getJournalId());
			case PLN_PLUGIN_DEPOSIT_OBJECT_ARTICLE:
				$articleDao =& DAORegistry::getDAO('ArticleDAO');
				$content = $articleDao->getArticle($content_id,$this->getJournalId());
			default:
		}
		return $content;
	}
	function setContent(&$content) {
		
		switch (get_class($content)) {
			case PLN_PLUGIN_DEPOSIT_OBJECT_ISSUE:
			case PLN_PLUGIN_DEPOSIT_OBJECT_ARTICLE:
				$content_type = get_class($content);
				$content_id = $content->getId();
				$this->setData('content_id', $content_id);
				$this->setData('content_type', $content_type);
				break;
			default:
		}
		
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
	* Get/Set deposit id
	*/
	function getDepositId() {
		return $this->getData('deposit_id');
	}
	function setDepositId($depositId) {
		$this->setData('deposit_id', $depositId);
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

}

?>

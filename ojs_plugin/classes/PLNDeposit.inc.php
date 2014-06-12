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

import('classes.article.SuppFile');

class PLNDeposit extends DataObject {

	function PLNDeposit() {
		parent::DataObject();
	}

	//
	// Get/set methods
	//




	/**
	* Deposit content (article or issue)
	*/
	function getContent() {
		$content_id = $this->getData('content_id');
		$content_type = $this->getData('content_type');
		return $this->getData('content_id');
	}
	function setContent($content) {
		$this->setData('id', $depositId);
	}

	/**
	* Submission id
	*/
	function getSubmissionId() {
		return $this->getData('submissionId');
	}
	function setSubmissionId($submissionId) {
		$this->setData('submissionId', $submissionId);
	}


	/**
	* Content source URI
	*/
	function getContentSourceUri() {
	return $this->getData('contentSourceUri');
	}
	function setContentSourceUri($contentSourceUri) {
	$this->setData('contentSourceUri', $contentSourceUri);
	}


}

?>

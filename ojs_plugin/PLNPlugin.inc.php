<?php

/**
 * @file plugins/generic/pln/PLNPlugin.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v3. For full terms see the file docs/COPYING.
 *
 * @class PLNPlugin
 * @ingroup plugins_generic_pln
 *
 * @brief PLN plugin class
 */

import('lib.pkp.classes.plugins.GenericPlugin');

define('PLN_PLUGIN_HTTP_STATUS_OK', 200);
define('PLN_PLUGIN_HTTP_STATUS_CREATED', 201);

class PLNPlugin extends GenericPlugin {

	/**
	 * Constructor
	 */
	function PLNPlugin() {
		parent::GenericPlugin();
	}

	/**
	 * @see PKPPlugin::register()
	 * @return boolean true iff success
	 */
	function register($category, $path) {
		$success = parent::register($category, $path);
		$this->addLocaleData();

		// sitewide function:
		$this->registerDAOs();
		
		// Delete all plug-in data for a journal when the journal is deleted
		HookRegistry::register('JournalDAO::deleteJournalById', array($this, 'deleteJournalById'));

		if ($success && $this->getEnabled()) {

		}
		
		return $success;
	}

	function getDisplayName() {
		return __('plugins.generic.pln.displayName');
	}

	function getDescription() {
		return __('plugins.generic.pln.description');
	}

	function getInstallSchemaFile() {
		return $this->getPluginPath() . '/schema.xml';
	}

	function getHandlerPath() {
		return $this->getPluginPath() . '/pages';
	}
  
	function getTemplatePath() {
		return parent::getTemplatePath() . '/templates';
	}
	
	function getContextSpecificPluginSettingsFile() {
		return $this->getPluginPath() . '/settings.xml';
	}

	/**
	 * Instantiate and register the DAOs.
	 */
	function registerDAOs() {
		$this->import('classes.DepositDAO');
		$this->import('classes.DepositObjectDAO');
		
		$depositDao = new DepositDAO($this->getName());
		DAORegistry::registerDAO('DepositDAO', $depositDao);
		
		$depositObjectDao = new DepositObjectDAO($this->getName());
		DAORegistry::registerDAO('DepositObjectDAO', $depositObjectDao);
	}
	
	/**
	 * Delete all plug-in data for a journal when the journal is deleted
	 * @param $hookName string (JournalDAO::deleteJournalById)
	 * @param $args array (JournalDAO, journalId)
	 * @return boolean false to continue processing subsequent hooks
	 */
	function deleteJournalById($hookName, $params) {
		$journalId = $params[1];
		$depositDao =& DAORegistry::getDAO('DepositDAO');
		//TODO: $depositDao->deleteByJournalId($journalId);
		$depositObjectDao =& DAORegistry::getDAO('DepositObjectDAO');
		//TODO: $depositObjectDao->deleteByJournalId($journalId);
		return false;
	}

	/**
	 * Display verbs for the management interface.
	 */
	function getManagementVerbs() {

	}

	/**
	* Execute a management verb on this plugin
	* @param $verb string
	* @param $args array
	* @param $message string Result status message
	* @param $messageParams array Parameters for the message key
	* @return boolean
	*/
	function manage($verb, $args, &$message, &$messageParams) {

	}
  
	/**
	 * Hook callback: add data citation to submissions, published articles, and
	 * reading tools.
	 */
	function handleTemplateDisplay($hookName, $args) {

	}
  
	/**
	 * Request service document at specified URL
	 * @param $journal_id int The journal id for the service document we wish to fetch
	 */
	function getServiceDocument($journal_id) {
		
		//if this journal hasn't been assigned a uuid yet, assign one
		if (!$this->getSetting($journal_id, 'uuid')) {
			$this->updateSetting($journal_id, 'uuid', $this->_newUUID());
		}
		
		//set the service document url we'll need
		$pln_networks = json_decode($this->getSetting($journal_id, 'pln_networks'));
		$pln_network = $this->getSetting($journal_id, 'pln_network');
		$this->updateSetting($journal_id,'pln_sd_iri', 'http://' . $pln_networks[$pln_network] . '/api/sword/2.0/sd-iri');
		
		// do an http get and retrieve the service document for this journal
		$ch = curl_init(); 
		curl_setopt($ch, CURLOPT_URL, $this->getSetting($deposit->getJournalId(), 'pln_sd_iri')); 
		curl_setopt($ch, CURLOPT_RETURNTRANSER, FALSE);
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, TRUE);
		curl_setopt($ch, CURLOPT_HTTPHEADER, array('On-Behalf-Of: '.$this->getSetting($journal_id, 'uuid')));
		$http_result = curl_exec($ch);
		$http_status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
		$http_error = curl_error($ch);
		curl_close ($ch);
		
		// stop here if we didn't get an OK
		if ($http_status != PLN_PLUGIN_HTTP_STATUS_OK) return $http_status;
		
		// load up the xml response to look for the collection url
		$service_document = new DOMDocument();
		$service_document->loadXML($http_result);
		
		$collections = $service_document->getElementsByTagName('collection');
		
		if ($collections->length()==0) return FALSE;
		
		// updating our settings with the current collection url
		foreach ($collections as $collection) {
			$this->updateSetting($journal_id,'pln_col_iri', $colletion->attributes->getNamedItem("href")->nodeValue);
		}
		
		return PLN_PLUGIN_HTTP_STATUS_OK;
	} 

	/**
	 * Transfer a deposit document to the appropriate collection url
	 * @param $deposit Deposit The deposit to transfer
	 */
	function transfer($deposit) {
		$post_fields = array('file_contents'=>'@'.$deposit->getPackagePath.DIRECTORY_SEPARATOR.PLN_PLUGIN_PACKAGE_FILE);
		$ch = curl_init(); 
		curl_setopt($ch, CURLOPT_URL, $this->getSetting($deposit->getJournalId(), 'pln_col_iri')); 
		curl_setopt($ch, CURLOPT_RETURNTRANSER, FALSE);
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, TRUE);
		curl_setopt($ch, CURLOPT_UPLOAD, TRUE);
		curl_setopt($ch, CURLOPT_POST, TRUE); 
		curl_setopt($ch, CURLOPT_POSTFIELDS, $post_fields); 
		$result = curl_exec($ch); 
		$error = curl_error($ch);
		curl_close ($ch);
	}

	/**
	 * Create a new UUID
	 */
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

<?php

/**
 * @file plugins/generic/pln/classes/tasks/PLNPluginDepositor.inc.php
 *
 * Copyright (c) 2013-2014 Simon Fraser University Library
 * Copyright (c) 2003-2014 John Willinsky
 * Distributed under the GNU GPL v2. For full terms see the file docs/COPYING.
 *
 * @class PLNPluginDepositor
 * @ingroup plugins_generic_pln_tasks
 *
 * @brief Class to perform automated deposits of PLN object.
 */

import('lib.pkp.classes.scheduledTask.ScheduledTask');

class PLNPluginDepositor extends ScheduledTask {
	
	var $_plugin;
	
	var $_pluginName;
	
	/**
	 * Constructor.
	 */
	function PLNPluginDepositor() {
		parent::ScheduledTask();
		
		$this->_plugin =& PluginRegistry::getPlugin('generic', 'plnplugin');
		
		if ($this->_plugin) {
			$this->_pluginName = $this->_plugin->getName();
			$this->_plugin->registerDAOs();
		}
	}

	/**
	 * @see ScheduledTask::getName()
	 */
	function getName() {
		return __('plugins.generic.pln.depositorTask.name');
	}

	/**
	 * @see ScheduledTask::executeActions()
	 */
	function executeActions() {
		
		if ($this->_plugin) {
			
			// Get all journals
			$journalDao =& DAORegistry::getDAO('JournalDAO');
			$depositDao =& DAORegistry::getDAO('DepositDAO');
			$depositObjectDao =& DAORegistry::getDAO('DepositObjectDAO');
			
			$journals =& $journalDao->getJournals(true);
			
			// For all journals
			while ($journal =& $journals->next()) {
				
				if ($this->_plugin->getSetting($journal->getId(), 'enabled')) {
					
					// get the sword service document
					$sd_result = $this->_plugin->getServiceDocument($journal->getId());
					
					// if for some reason we didn't get a valid reponse, move along
					if ($sd_result != PLN_PLUGIN_HTTP_STATUS_OK) continue;
					
					// Get all objects that haven't been assigned to a deposit and make a new deposit for them
					$newObjects =& $depositObjectDao->getNew();
					
					foreach ($newObjects as $newObjectKey => $newObject) {
						if ($newObject->getContentType() == PLN_PLUGIN_DEPOSIT_OBJECT_ISSUE) {
							$newDeposit = new Deposit();
							$depositDao->insertDeposit($newDeposit);
							$newObject->setDepositId($newDeposit->getId());
							$depositObjectDao->updateDepositObject($newObject);
							unset($newObjects[$newObjectKey]);
						}
					}
					
					// Get the new object threshold per deposit and split the remaining objects into arrays of that size
					$objectThreshold = $this->_plugin->getSetting($journal->getId(), 'object_threshold');
					
					foreach (array_chunk($newObjects,$objectThreshold) as $newObjectArray) {
						
						// the last array will have the remainder - only create a deposit for the complete threshold
						if (count($newObjectArray) == $objectThreshold) {
							
							//create a new deposit
							$newDeposit = new Deposit();
							$depositDao->insertDeposit($newDeposit);
							
							// add each object to the deposit
							foreach ($newObjectArray as $newObject) {
								$newObject->setDepositId($newDeposit->getId());
								$depositObjectDao->updateDepositObject($newObject);
							}
						}
					}
					
					unset($newObjects);
					
					// regenerate all the deposits for which we need to update content
					$fileManager = new PublicFileManager();
					$path = $fileManager->getJournalFilesPath($journal->getId()) . DIRECTORY_SEPARATOR . PLN_PLUGIN_PUBLIC_FOLDER . DIRECTORY_SEPARATOR;
					
					foreach ($depositDao->getNeedPackaging() as $deposit) {
						if (!$deposit->getPackagePath()) {
							$deposit->setPackagePath($path . $deposit->getUUID());
							$depositDao->updateDeposit($deposit);
						}
						$deposit->generatePackage();
						$deposit->generateAtom($this->_plugin->getSetting($journal->getId(), 'checksum_type'));
						$deposit->setStatus(PLN_PLUGIN_DEPOSIT_STATUS_PACKAGED);
						$deposit->setLastStatusDate(new DateTime());
						$depositDao->updateDeposit($deposit);
					}
					
					//transfer deposits we need to send to the pln
					$depositQueue = $depositDao->getNeedTransferring();
					
					foreach ($depositQueue as $deposit) {
						$result = $this->_plugin->transfer($deposit);
						if (($result == PLN_PLUGIN_HTTP_STATUS_OK) || ($result == PLN_PLUGIN_HTTP_STATUS_CREATED)) {
							$deposit->setStatus(PLN_PLUGIN_DEPOSIT_STATUS_TRANSFERRED);
							$deposit->setLastStatusDate(new DateTime());
							$depositDao->updateDeposit($deposit);
						}
					}
					
					
				}
				unset($journal);
			}
			return true;
		}
		return false;
	}

}

?>
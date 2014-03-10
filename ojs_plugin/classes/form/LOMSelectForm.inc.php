<?php

/**
 * @file plugins/generic/dataverse/DataverseSelectForm.inc.php
 *
 * Copyright (c) 2003-2013 John Willinsky
 * Distributed under the GNU GPL v2. For full terms see the file docs/COPYING.
 *
 * @class DataverseSelectForm
 * @ingroup plugins_generic_dataverse
 *
 * @brief Form for journal managers to provide DVN account for depositing files
 */
import('lib.pkp.classes.form.Form');

class DataverseSelectForm extends Form {

  /** @var $_plugin DataversePlugin */
  var $_plugin;

  /** @var $_journalId int */
  var $_journalId;

  /**
   * Constructor
   * @param $plugin DataversePlugin
   * @param $journalId int
   */
  function DataverseSelectForm(&$plugin, $journalId) {
    $this->_plugin =& $plugin;
    $this->_journalId = $journalId;
    parent::Form($plugin->getTemplatePath() . 'dataverseSelectForm.tpl');
    $this->addCheck(new FormValidator($this, 'dataverse', FORM_VALIDATOR_REQUIRED_VALUE, 'plugins.generic.dataverse.settings.dataverseRequired'));    
    $this->addCheck(new FormValidatorPost($this));    
  }

  /**
   * Initialize form data.
   */
  function initData() {
    // Get service document
    $sd = $this->_plugin->getServiceDocument(
            $this->_plugin->getSetting($this->_journalId, 'sdUri'),
            $this->_plugin->getSetting($this->_journalId, 'username'),
            $this->_plugin->getSetting($this->_journalId, 'password'),     
            '' // on behalf of
          );
    
    $dataverses = array();
    if (isset($sd)) {
      foreach ($sd->sac_workspaces as $workspace) {
        foreach ($workspace->sac_collections as $collection) {
          $dataverses["$collection->sac_href"] = "$collection->sac_colltitle";
        }
      }
    }
    /** @fixme add notice to check connection settings if no Dataverses found */
    $this->setData('dataverses', $dataverses);
    
    $dataverseUri = $this->_plugin->getSetting($this->_journalId, 'dvUri');
    if (isset($dataverseUri) and array_key_exists($dataverseUri, $dataverses)) {
      $this->setData('dataverseUri', $dataverseUri);
    }      
  }

  /**
   * Assign form data to user-submitted data.
   */
  function readInputData() {
    $this->readUserVars(array('dataverse'));
  }

  /**
   * Save settings.
   */
  function execute() {
    $this->_plugin->updateSetting($this->_journalId, 'dvUri', $this->getData('dataverse'), 'string');
  }
}
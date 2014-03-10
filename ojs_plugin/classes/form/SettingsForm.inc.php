<?php

/**
 * @file plugins/generic/dataverse/SettingsForm.inc.php
 *
 * Copyright (c) 2003-2013 John Willinsky
 * Distributed under the GNU GPL v2. For full terms see the file docs/COPYING.
 *
 * @class SettingsForm
 * @ingroup plugins_generic_dataverse
 *
 * @brief Form for journal managers to modify Dataverse plugin settings
 */

import('lib.pkp.classes.form.Form');
import('plugins.generic.tinymce.TinyMCEPlugin');

class SettingsForm extends Form {

  /** @var $journalId int */
  var $_journalId;

  /** @var $plugin object */
  var $_plugin;

  /**
   * Constructor
   * @param $plugin object
   * @param $journalId int
   */
  function settingsForm(&$plugin, $journalId) {
    $this->_journalId = $journalId;
    $this->_plugin =& $plugin;
    
    // Citation formats
    $this->_citationFormats = array(
        DATAVERSE_PLUGIN_CITATION_FORMAT_APA => __('plugins.generic.dataverse.settings.citationFormat.apa'),
      );
    
    // Study release options
    $this->_studyReleaseOptions = array(
        DATAVERSE_PLUGIN_RELEASE_ARTICLE_ACCEPTED => __('plugins.generic.dataverse.settings.studyReleaseSubmissionAccepted'),
        DATAVERSE_PLUGIN_RELEASE_ARTICLE_PUBLISHED => __('plugins.generic.dataverse.settings.studyReleaseArticlePublished')
    );    

    // Public id plugins
    $this->_pubIdTypes = array();
    $pubIdPlugins =& PluginRegistry::loadCategory('pubIds', true, $this->_journalId);
		if (is_array($pubIdPlugins)) {
			foreach ($pubIdPlugins as $pubIdPlugin) {
        // Load the formatter
        $this->_pubIdTypes[$pubIdPlugin->getName()] = $pubIdPlugin->getDisplayName();
      }
		}            
    
    parent::Form($plugin->getTemplatePath() . 'settingsForm.tpl');
    $this->addCheck(new FormValidatorPost($this));
    $this->addCheck(new FormValidator($this, 'dataAvailability', FORM_VALIDATOR_REQUIRED_VALUE, 'plugins.generic.dataverse.settings.dataAvailabilityRequired'));
    $this->addCheck(new FormValidatorCustom($this, 'termsOfUse', FORM_VALIDATOR_REQUIRED_VALUE, 'plugins.generic.dataverse.settings.termsOfUseRequired', array(&$this, '_validateTermsOfUse')));
    $this->addCheck(new FormValidatorCustom($this, 'termsOfUse', FORM_VALIDATOR_REQUIRED_VALUE, 'plugins.generic.dataverse.settings.dataverseTermsOfUseError', array(&$this, '_validateDataverseTermsOfUse'))); 
    $this->addCheck(new FormValidatorPost($this));    
  }

  /**
   * Initialize form data.
   */
  function initData() {
    $plugin =& $this->_plugin;

    // Initialize from plugin settings
    foreach (array_keys($this->_getFormFields()) as $field) {
      $this->setData($field, $plugin->getSetting($this->_journalId, $field));
    }
    
    // Get citation formats
    $this->setData('citationFormats', $this->_citationFormats);
    $citationFormat = $this->_plugin->getSetting($this->_journalId, 'citationFormat');
    if (isset($citationFormat) && array_key_exists($citationFormat, $this->_citationFormats)) {
      $this->setData('citationFormat', $citationFormat);
    }
    
    // Get pub id format plugins
    $this->setData('pubIdTypes', $this->_pubIdTypes);
    $pubIdPlugin = $this->_plugin->getSetting($this->_journalId, 'pubIdPlugin');
    if (isset($pubIdPlugin) && array_key_exists($pubIdPlugin, $pubIdTypes)) {
      $this->setData('pubIdPlugin', $pubIdPlugin);
    } 
    

    $this->setData('studyReleaseOptions', $this->_studyReleaseOptions);
    $studyRelease = $this->_plugin->getSetting($this->_journalId, 'studyRelease');
    if (array_key_exists($studyRelease, $this->_studyReleaseOptions)) {
      $this->setData('studyRelease', $studyRelease);
    }
    
  }

  /**
   * Assign form data to user-submitted data.
   */
  function readInputData() {
    $this->readUserVars(array_keys($this->_getFormFields()));
  }
  
	/**
	 * @see Form::fetch()
	 */
	function fetch(&$request, $template = null, $display = false) {
		$sectionDao =& DAORegistry::getDAO('SectionDAO');
		$sections =& $sectionDao->getJournalSections($this->_journalId);
    
		$templateMgr =& TemplateManager::getManager($request);
		$templateMgr->assign('sections', $sections->toArray());
    $templateMgr->assign('citationFormats', $this->_citationFormats);
    $templateMgr->assign('pubIdTypes', $this->_pubIdTypes); 
    $templateMgr->assign('studyReleaseOptions', $this->_studyReleaseOptions);
    
		parent::fetch($request, $template, $display);
	}  

  /**
   * Save settings.
   */
  function execute() { 
    $plugin =& $this->_plugin;
    $formFields = $this->_getFormFields();

    foreach ($formFields as $field => $type) {
      $plugin->updateSetting($this->_journalId, $field, $this->getData($field), $type);
    }
    
    // Store DV TOU as a backup if not accessible via API. Update when fetched from API.
    if ($this->getData('dvTermsOfUse')) {
      $plugin->updateSetting($this->_journalId, 'dvTermsOfUse', $this->getData('dvTermsOfUse'), 'string');
    }
  }
  
  /**
   * Opt to fetch DV TOU *or* provide custom TOU.
   * @return bool
   */
  function _validateTermsOfUse() {
    // If JM chooses to define own terms, verify that terms of use are provided 
    return $this->getData('fetchTermsOfUse') === "1" || $this->getData('termsOfUse');
  }
  
  /**
   * If TOU to be fetched from DV, verify TOU are available
   * @return bool
   */
  function _validateDataverseTermsOfUse() {
    if ($this->getData('fetchTermsOfUse') === "0") return true;

    // Otherwise, try to fetch terms of use
    $dvTermsOfUse = $this->_plugin->getTermsOfUse();
    if (!$dvTermsOfUse) return false;
    
    // Store for faster retrieval on execute
    $this->setData('dvTermsOfUse', $dvTermsOfUse);
    return true;
  }
  
  /**
   * Get terms of use of Dataverese configured for this journal
   * @return string
   */

  
	/**
   * Return the field names of this form.
   * @return array
   */
  function _getFormFields() {
    $formFields = array(
        'dataAvailability' => 'string',
        'fetchTermsOfUse' => 'bool',
        'termsOfUse' => 'string',
        'citationFormat' => 'string',
        'pubIdPlugin' => 'string',
        'requireData' => 'bool',
        'studyRelease' => 'int'
    );
    return $formFields;
  }  

}
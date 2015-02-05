
SET FOREIGN_KEY_CHECKS=0; -- MUST ENABLE THIS BELOW.
SET NAMES 'UTF8';
SET default_storage_engine='InnoDB';

ALTER SCHEMA
    DEFAULT CHARACTER SET UTF8
    DEFAULT COLLATE UTF8_GENERAL_CI ;

DROP TABLE IF EXISTS `journals`;
CREATE TABLE `journals` (
    `journal_uuid` char(36) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
    `contact_date` datetime DEFAULT CURRENT_TIMESTAMP,
    `notified_date` datetime DEFAULT NULL,
    `title` varchar(256) NOT NULL,
    `issn` varchar(256) NOT NULL,
    `journal_url` varchar(256) NOT NULL,
    `journal_status` varchar(16) NOT NULL DEFAULT 'healthy',
    `contact_email` varchar(256) NOT NULL,
    `publisher_name` varchar(255) NOT NULL,
    `publisher_url` varchar(255) NOT NULL,
    PRIMARY KEY (`journal_uuid`)
)  ENGINE=INNODB CHARACTER SET=UTF8 COLLATE = UTF8_GENERAL_CI;

ALTER TABLE `journals`
  ADD INDEX `journal_status_idx` (`journal_status` ASC),
  ADD INDEX `journal_contact_idx` (`contact_date` DESC);

DROP TABLE IF EXISTS `deposits`;
CREATE TABLE `deposits` (
    `deposit_uuid` CHAR(36) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
    `journal_uuid` CHAR(36) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
    `date_deposited` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `deposit_action` varchar(5) NOT NULL,
    `deposit_volume` varchar(256) NOT NULL,
    `deposit_issue` varchar(256) NOT NULL,
    `deposit_pubdate` varchar(10) NOT NULL,
    `deposit_sha1` varchar(40) NOT NULL,
    `deposit_url` varchar(256) NOT NULL,
    `deposit_size` int(11) NOT NULL,
    `processing_state` varchar(32) NOT NULL,
    `outcome` varchar(255) NOT NULL,
    `pln_state` varchar(255) NOT NULL,
    `deposited_lom` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    `deposit_receipt` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`deposit_uuid`)
)  ENGINE=INNODB CHARACTER SET=UTF8 COLLATE = UTF8_GENERAL_CI;

ALTER TABLE `deposits`
  ADD INDEX `deposits_proc_idx` (`processing_state` ASC),
  ADD INDEX `deposits_outcome_idx` (`outcome` ASC),
  ADD CONSTRAINT `deposits_fk1` FOREIGN KEY (`journal_uuid`) REFERENCES `journals` (journal_uuid);

DROP TABLE IF EXISTS `microservices`;
CREATE TABLE `microservices` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `deposit_uuid` CHAR(36) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
    `microservice` varchar(255) NOT NULL,
    `started_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    `finished_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    `outcome` varchar(255) NOT NULL,
    `error` longtext NOT NULL,
    PRIMARY KEY (`id`)
)  ENGINE=INNODB CHARACTER SET=UTF8 COLLATE = UTF8_GENERAL_CI;

ALTER TABLE `microservices`
  ADD CONSTRAINT `microservices_fk1` FOREIGN KEY (`deposit_uuid`) REFERENCES `deposits` (deposit_uuid);

DROP TABLE IF EXISTS `terms_of_use`;
CREATE TABLE `terms_of_use` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `weight` int(11) NOT NULL DEFAULT '0',
    `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `key_code` varchar(256) NOT NULL,
    `lang_code` varchar(8) NOT NULL,
    `content` text NOT NULL,
    PRIMARY KEY (`id`)
)  ENGINE=INNODB CHARACTER SET=UTF8 COLLATE = UTF8_GENERAL_CI;

INSERT INTO `terms_of_use` (`weight`, `created`, `key_code`, `lang_code`, `content`) VALUES
    (6,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.jm_has_authority','en-US','I have the legal and contractual authority to include this journal\'s content in a secure preservation network and, if and when necessary, to make the content available in the PKP PLN.'),
    (3,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.pkp_can_use_cc_by','en-US','I agree to allow the PKP-PLN to make post-trigger event content available under the CC-BY (or current equivalent) license.'),
    (2,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.pkp_can_use_address','en-US','I agree to allow the PKP-PLN to include this journal\'s title and ISSN, and the email address of the Primary Contact, with the preserved journal content.'),
    (5,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.licensing_is_current','en-US','I confirm that licensing information pertaining to articles in this journal is accurate at the time of publication.'),
    (4,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.terms_may_be_revised','en-US','I acknowledge these terms may be revised from time to time and I will be required to review and agree to them each time this occurs.'),
    (0,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.jm_will_not_violate','en-US','I agree not to violate any laws and regulations that may be applicable to this network and the content.'),
    (1,'2014-09-21 00:00:00','plugins.generic.pln.terms_of_use.pkp_may_not_preserve','en-US','I agree that the PKP-PLN reserves the right, for whatever reason, not to preserve or make content available.');

SET FOREIGN_KEY_CHECKS=1; -- MUST ENABLE THIS BELOW.

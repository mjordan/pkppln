-- MySQL dump 10.13  Distrib 5.6.20, for osx10.8 (x86_64)
--
-- Host: localhost    Database: pkppln
-- ------------------------------------------------------
-- Server version	5.6.20-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `deposits`
--

DROP TABLE IF EXISTS `deposits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deposits` (
  `deposit_uuid` char(36) CHARACTER SET ascii NOT NULL,
  `journal_uuid` char(36) CHARACTER SET ascii NOT NULL,
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
  PRIMARY KEY (`deposit_uuid`),
  KEY `deposits_proc_idx` (`processing_state`),
  KEY `deposits_outcome_idx` (`outcome`),
  KEY `deposits_fk1` (`journal_uuid`),
  CONSTRAINT `deposits_fk1` FOREIGN KEY (`journal_uuid`) REFERENCES `journals` (`journal_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deposits`
--
-- ORDER BY:  `deposit_uuid`

LOCK TABLES `deposits` WRITE;
/*!40000 ALTER TABLE `deposits` DISABLE KEYS */;
/*!40000 ALTER TABLE `deposits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journals`
--

DROP TABLE IF EXISTS `journals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `journals` (
  `journal_uuid` char(36) CHARACTER SET ascii NOT NULL,
  `contact_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `notified_date` datetime DEFAULT NULL,
  `title` varchar(256) NOT NULL,
  `issn` varchar(256) NOT NULL,
  `journal_url` varchar(256) NOT NULL,
  `journal_status` varchar(16) NOT NULL DEFAULT 'healthy',
  `contact_email` varchar(256) NOT NULL,
  `publisher_name` varchar(255) NOT NULL,
  `publisher_url` varchar(255) NOT NULL,
  PRIMARY KEY (`journal_uuid`),
  KEY `journal_status_idx` (`journal_status`),
  KEY `journal_contact_idx` (`contact_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journals`
--
-- ORDER BY:  `journal_uuid`

LOCK TABLES `journals` WRITE;
/*!40000 ALTER TABLE `journals` DISABLE KEYS */;
/*!40000 ALTER TABLE `journals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `microservices`
--

DROP TABLE IF EXISTS `microservices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `microservices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `deposit_uuid` char(36) CHARACTER SET ascii NOT NULL,
  `microservice` varchar(255) NOT NULL,
  `started_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `finished_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `outcome` varchar(255) NOT NULL,
  `error` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `microservices_fk1` (`deposit_uuid`),
  CONSTRAINT `microservices_fk1` FOREIGN KEY (`deposit_uuid`) REFERENCES `deposits` (`deposit_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `microservices`
--
-- ORDER BY:  `id`

LOCK TABLES `microservices` WRITE;
/*!40000 ALTER TABLE `microservices` DISABLE KEYS */;
/*!40000 ALTER TABLE `microservices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `terms_of_use`
--

DROP TABLE IF EXISTS `terms_of_use`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `terms_of_use` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `weight` int(11) NOT NULL DEFAULT '0',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `key_code` varchar(256) NOT NULL,
  `lang_code` varchar(8) NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `terms_of_use`
--
-- ORDER BY:  `id`

LOCK TABLES `terms_of_use` WRITE;
/*!40000 ALTER TABLE `terms_of_use` DISABLE KEYS */;
INSERT INTO `terms_of_use` (`id`, `weight`, `created`, `key_code`, `lang_code`, `content`) VALUES (1,6,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.jm_has_authority','en-US','I have the legal and contractual authority to include this journal\'s content in a secure preservation network and, if and when necessary, to make the content available in the PKP PLN.'),(2,3,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.pkp_can_use_cc_by','en-US','I agree to allow the PKP-PLN to make post-trigger event content available under the CC-BY (or current equivalent) license.'),(3,2,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.pkp_can_use_address','en-US','I agree to allow the PKP-PLN to include this journal\'s title and ISSN, and the email address of the Primary Contact, with the preserved journal content.'),(4,5,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.licensing_is_current','en-US','I confirm that licensing information pertaining to articles in this journal is accurate at the time of publication.'),(5,4,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.terms_may_be_revised','en-US','I acknowledge these terms may be revised from time to time and I will be required to review and agree to them each time this occurs.'),(6,0,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.jm_will_not_violate','en-US','I agree not to violate any laws and regulations that may be applicable to this network and the content.'),(7,1,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.pkp_may_not_preserve','en-US','I agree that the PKP-PLN reserves the right, for whatever reason, not to preserve or make content available.');
/*!40000 ALTER TABLE `terms_of_use` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-03-04 13:51:31

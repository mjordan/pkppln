-- MySQL dump 10.13  Distrib 5.6.15, for osx10.7 (x86_64)
--
-- Host: localhost    Database: pkppln
-- ------------------------------------------------------
-- Server version	5.6.15

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
-- Table structure for table `journals`
--

DROP TABLE IF EXISTS `journals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `journals` (
  `journal_uuid` char(36) CHARACTER SET ascii NOT NULL,
  `contact_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
) ENGINE=InnoDB AUTO_INCREMENT=228 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-02-24 15:30:57

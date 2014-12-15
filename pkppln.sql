-- MySQL dump 10.13  Distrib 5.6.20, for osx10.8 (x86_64)
--
-- Host: localhost    Database: pkpplntest
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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` varchar(5) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_volume` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_issue` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_pubdate` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `date_deposited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `journal_uuid` varchar(38) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `sha1_value` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_url` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `size` int(11) NOT NULL,
  `processing_state` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `outcome` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `pln_state` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `deposited_lom` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deposits`
--
-- ORDER BY:  `id`

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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `journal_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `title` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `issn` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `journal_url` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `contact_email` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `date_deposited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=291 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journals`
--
-- ORDER BY:  `id`

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
  `microservice` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `started_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `finished_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `outcome` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `error` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
  `current_version` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `key` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `language` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `text` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=496 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `terms_of_use`
--
-- ORDER BY:  `id`

LOCK TABLES `terms_of_use` WRITE;
/*!40000 ALTER TABLE `terms_of_use` DISABLE KEYS */;
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

-- Dump completed on 2014-12-15 13:43:18

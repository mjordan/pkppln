-- phpMyAdmin SQL Dump
-- version 4.0.6deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 22, 2014 at 02:43 PM
-- Server version: 5.5.37-0ubuntu0.13.10.1-log
-- PHP Version: 5.5.3-1ubuntu2.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `pkppln`
--

-- --------------------------------------------------------

--
-- Table structure for table `deposits`
--

CREATE TABLE IF NOT EXISTS `deposits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` varchar(5) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_details` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
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
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=58 ;

-- --------------------------------------------------------

--
-- Table structure for table `journals`
--

CREATE TABLE IF NOT EXISTS `journals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `journal_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `title` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `issn` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `contact_email` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `date_deposited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `microservices`
--

CREATE TABLE IF NOT EXISTS `microservices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `microservice` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `started_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `finished_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `outcome` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `error` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=187 ;

-- --------------------------------------------------------

--
-- Table structure for table `terms_of_use`
--

CREATE TABLE IF NOT EXISTS `terms_of_use` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `key` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `language` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `text` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- phpMyAdmin SQL Dump
-- version 4.0.6deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 18, 2014 at 03:28 PM
-- Server version: 5.5.35-0ubuntu0.13.10.2
-- PHP Version: 5.5.3-1ubuntu2.2

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
-- Table structure for table `archived_issues`
--

CREATE TABLE IF NOT EXISTS `archived_issues` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` varchar(5) COLLATE utf8_unicode_ci NOT NULL,
  `journal_manager_email` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_uuid` varchar(38) COLLATE utf8_unicode_ci NOT NULL,
  `date_deposited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `journal_uuid` varchar(38) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `sha1_value` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `issue_url` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `size` int(11) NOT NULL,
  `status` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `harvested` timestamp NULL DEFAULT NULL,
  `deposited_lom` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=40 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

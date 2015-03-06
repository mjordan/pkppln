-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Table `journals`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `journals` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `journal_uuid` CHAR(36) CHARACTER SET 'ascii' NOT NULL,
  `contact_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `notified_date` DATETIME,
  `title` VARCHAR(256) NOT NULL,
  `issn` VARCHAR(256) NOT NULL,
  `journal_url` VARCHAR(256) NOT NULL,
  `journal_status` VARCHAR(16) NOT NULL DEFAULT 'healthy',
  `contact_email` VARCHAR(256) NOT NULL,
  `publisher_name` VARCHAR(255) NOT NULL,
  `publisher_url` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `journal_status_idx` (`journal_status` ASC),
  INDEX `journal_contact_idx` (`contact_date` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `deposits`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `deposits` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `journal_id` INT NOT NULL,
  `file_uuid` CHAR(36) NOT NULL,
  `deposit_uuid` CHAR(36) CHARACTER SET 'ascii' NOT NULL,
  `date_deposited` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deposit_action` VARCHAR(5) NOT NULL,
  `deposit_volume` VARCHAR(256) NOT NULL,
  `deposit_issue` VARCHAR(256) NOT NULL,
  `deposit_pubdate` VARCHAR(10) NOT NULL,
  `deposit_sha1` VARCHAR(40) NOT NULL,
  `deposit_url` VARCHAR(256) NOT NULL,
  `deposit_size` INT(11) NOT NULL,
  `processing_state` VARCHAR(32) NOT NULL,
  `outcome` VARCHAR(255) NOT NULL,
  `pln_state` VARCHAR(255) NOT NULL,
  `deposited_lom` TIMESTAMP NULL DEFAULT NULL,
  `deposit_receipt` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `deposits_proc_idx` (`processing_state` ASC),
  INDEX `deposits_outcome_idx` (`outcome` ASC),
  INDEX `deposits_fk1` (`journal_id` ASC),
  UNIQUE INDEX `file_uuid_UNIQUE` (`file_uuid` ASC),
  CONSTRAINT `deposits_fk1`
    FOREIGN KEY (`journal_id`)
    REFERENCES `journals` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `microservices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `microservices` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `deposit_id` INT NOT NULL,
  `microservice` VARCHAR(255) NOT NULL,
  `started_on` DATETIME NOT NULL,
  `finished_on` DATETIME NOT NULL,
  `outcome` VARCHAR(255) NOT NULL,
  `error` LONGTEXT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `microservices_fk1` (`deposit_id` ASC),
  CONSTRAINT `microservices_fk1`
    FOREIGN KEY (`deposit_id`)
    REFERENCES `deposits` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `terms_of_use`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `terms_of_use` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `weight` INT(11) NOT NULL DEFAULT '0',
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `key_code` VARCHAR(256) NOT NULL,
  `lang_code` VARCHAR(8) NOT NULL,
  `content` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

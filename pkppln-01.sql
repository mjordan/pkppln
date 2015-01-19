ALTER TABLE `mypln`.`journals` 
ADD COLUMN `publisher_name` VARCHAR(255) NOT NULL AFTER `date_deposited`,
ADD COLUMN `publisher_url` VARCHAR(255) NOT NULL AFTER `publisher_name`;

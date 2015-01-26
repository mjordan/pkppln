ALTER TABLE `mypln`.`terms_of_use` 
ADD COLUMN `weight` INT(11) NOT NULL DEFAULT 0;
UPDATE `mypln`.`terms_of_use` SET weight=0;

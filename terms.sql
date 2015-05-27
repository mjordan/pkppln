LOCK TABLES `terms_of_use` WRITE;
INSERT INTO `terms_of_use` (`id`, `weight`, `created`, `key_code`, `lang_code`, `content`) VALUES 
(1,6,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.jm_has_authority','en-US','I have the legal and contractual authority to include this journal\'s content in a secure preservation network and, if and when necessary, to make the content available in the PKP PLN.'),
(2,3,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.pkp_can_use_cc_by','en-US','I agree to allow the PKP-PLN to make post-trigger event content available under the CC-BY (or current equivalent) license.'),
(3,2,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.pkp_can_use_address','en-US','I agree to allow the PKP-PLN to include this journal\'s title and ISSN, and the email address of the Primary Contact, with the preserved journal content.'),
(4,5,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.licensing_is_current','en-US','I confirm that licensing information pertaining to articles in this journal is accurate at the time of publication.'),
(5,4,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.terms_may_be_revised','en-US','I acknowledge these terms may be revised from time to time and I will be required to review and agree to them each time this occurs.'),
(6,0,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.jm_will_not_violate','en-US','I agree not to violate any laws and regulations that may be applicable to this network and the content.'),
(7,1,'2014-09-21 07:00:00','plugins.generic.pln.terms_of_use.pkp_may_not_preserve','en-US','I agree that the PKP-PLN reserves the right, for whatever reason, not to preserve or make content available.');
UNLOCK TABLES;

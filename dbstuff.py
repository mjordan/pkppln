import MySQLdb
import config

def db_instance(DB_NAME):
	db = MySQLdb.connect(host=config.LOCAL_DB_HOST, port=config.LOCAL_DB_PORT, user=config.LOCAL_DB_USER, passwd=config.LOCAL_DB_PASSWORD, db=DB_NAME)
	db.autocommit(True)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
#	nonDictCursor = db.cursor()
	return database_cursor

def create_table(database_cursor):

	sql = """
	SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
	SET time_zone = "+00:00";
	CREATE TABLE IF NOT EXISTS `archivedcontent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_deposited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `journal_uuid` varchar(38) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `sha1_value` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `issue_url` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
	""" % table_name

	database_cursor.execute(sql)

def add_db_entry(database_cursor):
	database_cursor.executemany("insert into archivedcontent values (%s)")
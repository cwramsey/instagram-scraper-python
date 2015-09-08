import pymysql.cursors
from loggingUtils import getLogger
from ConfigParser import SafeConfigParser

logger = getLogger(__name__)
config = SafeConfigParser()
config.read('./config.ini')

def dbConnect():
    """
        Um. Connects to the db.
    """
    global config

    connection = pymysql.connect(host=config.get('db', 'host'),
                    user=config.get('db', 'user'),
                    password=config.get('db', 'pass'),
                    port=config.get('db', 'port'),
                    db=config.get('db', 'db'),
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor)

    return connection

def dbCreateUserTable():
    """
        On script run, we should check to see if the table exists and create it if it doesn't.
        Makes things easy so we don't have to run any install type scripts.
    """

    global logger

    logger.info("Creating users table if it does not exist")
    con = dbConnect()
    query = "CREATE TABLE IF NOT EXISTS `users` ( \
          `id` bigint(100) unsigned NOT NULL, \
          `username` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL, \
          `fullname` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL, \
          `bio` text COLLATE utf8mb4_unicode_ci NOT NULL, \
          `website` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL, \
          `avatar` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL, \
          `count_media` int(10) unsigned NOT NULL, \
          `count_followers` int(10) unsigned NOT NULL, \
          `count_follows` int(10) unsigned NOT NULL, \
          `user_id` bigint(100) NOT NULL \
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; \
        ALTER TABLE `users` \
          ADD PRIMARY KEY (`id`); \
        ALTER TABLE `users` \
          MODIFY `id` bigint(100) unsigned NOT NULL AUTO_INCREMENT;"

    try:
        with con.cursor() as cursor:
            cursor.execute(query)

        con.commit()
    finally:
        con.close()




def dbSelectLast():
    """
        Pulls the most recent user from the list in case we're starting over again if something happens.
    """
    con = dbConnect()
    try:
        with con.cursor() as cursor:
            sql = "SELECT * FROM users ORDER BY ID DESC;"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
    finally:
        con.close()

def dbInsert(vals):
    """
        Arg: @list
        Inserts a user into the DB
    """

    con = dbConnect()
    try:
        with con.cursor() as cursor:
            sql = "INSERT INTO users (username, fullname, bio, website, avatar, count_media, count_followers, count_follows, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(sql, vals)

        con.commit()
    finally:
        con.close()

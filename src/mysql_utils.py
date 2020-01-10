import MySQLdb
from MySQLdb import IntegrityError, cursors

"""
CREATE DATABASE Twitter;
USE Twitter;

CREATE TABLE IF NOT EXISTS query(
 query_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
 entity VARCHAR(20) NOT NULL,
 source_type VARCHAR(20) NOT NULL,
 domain VARCHAR(20) NOT NULL,
 since DATETIME DEFAULT NULL,
 until DATETIME DEFAULT NULL,
 location VARCHAR(20),
 PRIMARY KEY (query_id),
 CONSTRAINT uc_query UNIQUE (entity, source_type, domain)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS queue(
 user_handle CHAR(20) NOT NULL,
 user_status TINYINT(1) DEFAULT 0,
 tweet_status TINYINT(1) DEFAULT 0,
 attempts INT(10) DEFAULT 0,
 last_attempted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 query_id INT(10) UNSIGNED NOT NULL,
 PRIMARY KEY (user_handle,query_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS user_query_log(
 user_handle CHAR(20) NOT NULL,
 query_id INT(10) UNSIGNED NOT NULL,
 PRIMARY KEY (user_handle,query_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS tweet_query_log(
 tweet_id BIGINT(20) UNSIGNED NOT NULL,
 query_id INT(10) UNSIGNED NOT NULL,
 PRIMARY KEY (tweet_id, query_id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS tweet
(
  tweet_id          BIGINT UNSIGNED                    NOT NULL
    PRIMARY KEY,
  user_id           BIGINT UNSIGNED                    NOT NULL,
  date              DATETIME                           NOT NULL,
  favorites         INT(10)                            NOT NULL,
  geo               VARCHAR(20)                        NULL,
  hashtags          VARCHAR(280)                       NOT NULL,
  mentions          VARCHAR(280)                       NOT NULL,
  permalink         VARCHAR(200)                       NULL,
  retweet_permalink VARCHAR(200)                       NULL,
  retweets          INT UNSIGNED                       NOT NULL,
  text              VARCHAR(280)                       NOT NULL,
  urls_contained    VARCHAR(280)                       NULL,
  actual_name       VARCHAR(50)                        NOT NULL,
  user_handle       VARCHAR(30)                        NULL,
  profile_image_url VARCHAR(200)                       NULL,
  last_updated      DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  reply_permalink VARCHAR(200)                       NULL,

)
  ENGINE = MyISAM
  CHARSET = utf8;

CREATE INDEX text
  ON tweet (text);

CREATE INDEX tweet_user_handle_index
  ON tweet (user_handle);

CREATE TABLE IF NOT EXISTS user (
  user_id BIGINT(20) UNSIGNED NOT NULL,
  user_handle VARCHAR(30) NOT NULL,
  created_at DATETIME,
  description VARCHAR(500) DEFAULT NULL,
  description_url VARCHAR(100) DEFAULT NULL,
  location VARCHAR(100) DEFAULT NULL,
  followers_count INT(10) UNSIGNED NOT NULL,
  likes_count INT(10) UNSIGNED NOT NULL,
  following_count INT(10) UNSIGNED NOT NULL,
  actual_name VARCHAR(100) NOT NULL,
  profile_image_url VARCHAR(200) NOT NULL,
  total_tweet_count INT(10) UNSIGNED DEFAULT 0,
  time_zone VARCHAR(120) DEFAULT NULL,
  query_id INT(10) UNSIGNED DEFAULT NULL,
  protected TINYINT(1) DEFAULT NULL,
  verified TINYINT(1) DEFAULT NULL,
  lang VARCHAR(50) DEFAULT NULL,
  geo_enabled TINYINT(1) DEFAULT NULL,
  utc_offset INT(10) DEFAULT NULL,
  last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-----------------------------------------------
Procedure and scheduling
------------------------------------------------

CREATE PROCEDURE update_count_in_query()
  BEGIN
    UPDATE query, queue SET query.user_count = (SELECT count(*) from queue where queue.query_id = query.query_id );
    UPDATE query,tweet_query_log SET tweet_count = (SELECT count(*) FROM tweet_query_log WHERE tweet_query_log.query_id = query.query_id);
  END;


SET GLOBAL event_scheduler = ON;
CREATE EVENT myevent
    ON SCHEDULE EVERY 1 HOUR
    DO
      CALL update_count_in_query();


ALTER TABLE user
ADD FULLTEXT INDEX description_index
(description, time_zone, location);
---------------------------------------------------------
"""


class MySqlUtils:

    def __init__(self, db_name='Twitter'):
        self.db_name = db_name
        self.db = MySQLdb.connect(db=self.db_name, host='52.172.205.54', user="ankur", password="ankur123",cursorclass=MySQLdb.cursors.DictCursor)
        #self.db = MySQLdb.connect(db=self.db_name, host='localhost', user="root", password="root123",cursorclass=MySQLdb.cursors.DictCursor)
        self.write_cursor = self.db.cursor(cursors.DictCursor)
        self.read_cursor = self.db.cursor(cursors.DictCursor)
        self.cursor = self.db.cursor(cursors.DictCursor)


    def dict_to_sql(self, data_dict, table_name):

        """
        :return:
        """
        placeholders = ', '.join(['%s'] * len(data_dict))
        columns = ', '.join(data_dict.keys())

        query = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table_name, columns, placeholders)
        try:
            self.cursor.execute(query, data_dict.values())
            self.db.commit()
        except IntegrityError as e:
            print(query)
            print(data_dict.values())
            print(e)
        except Exception as e:
            print(query)
            raise e

    def get_data(self, query):
        self.cursor.execute(query)
        response = self.cursor.fetchall()
        return response

    def get_one_row(self, query):
        # caching query
        if not self.cursor._executed:
            self.cursor.execute(query)
        elif self.cursor._executed.decode() != query:
            self.cursor.execute(query)
        response = self.cursor.fetchone()
        return response





    def close(self):
        """

        :return:
        """
        self.cursor.close()
        self.db.close()




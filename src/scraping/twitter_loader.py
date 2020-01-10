"""
author :- Deepak
obj    :- connecting database to various scrapers. Implements insertion into stealth's
            mysql schema.
input  :- data dictionary which contains the input to the query table.
output :-
TODO: Find an elegant fix to encoding decoding issues.
TODO: Cleaning and Refactoring DB code.
TODO: Optimize and further multiprocess scraping via GOT.
TODO: scrape followers using GOT approach.
      url=https://twitter.com/INCIndia/followers/users?include_available_features=1&include_entities=1&max_position=1592264930043186001&reset_error_state=false'
TODO: facebook scraping

"""
import os
import sys
import time
home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')

from src.mysql_utils import MySqlUtils
from src.scraping.twitter_scraper import TwitterScraper
from collections import defaultdict
from lib.GetOldTweets.got3 import manager as gotmanager
from src.scraping.got_patch import getJsonReponse, getTweets

from urllib import parse
import re

SHARDS = 10
handle_regex = re.compile('^[@a-zA-Z0-9_]+')

# Monkey Patching for a bug in GOT Library
gotmanager.TweetManager.getJsonReponse = getJsonReponse
gotmanager.TweetManager.getTweets = getTweets


class TwitterLoader:
    """ Runs one query at a time and stores the data in mysql tables.

    """

    def __init__(self, data=None):
        """data is a
        :param data: dictionary which contains a row of query_id, source_type, domain, since, until, location
        """
        self.query_id = None
        self.data_query = data
        if self.data_query is None:
            self.data_query = {}
        self.sql = MySqlUtils()
        self.sql_fetch = MySqlUtils()
        self.scraper = TwitterScraper()
        self.handles = None
        self.include_retweets = False
        self.include_replies = False
        self.shard_number = None

    def close(self):
        """

        :return:
        """
        self.scraper.close()
        self.sql.close()

    def insert_query(self):
        """ Insert to query table

        """
        self.sql.dict_to_sql(self.data_query, 'query')
        self.query_id = self.sql.cursor.lastrowid

    def insert_queue(self, url=None, followers_handle=None):
        """

        :return:
        """
        # Get Queue Data
        if  not followers_handle:
            self.scraper.login_to_twitter()
        # get the followers
        # TODO: Fix this.
        self.scraper.driver.get(url)
        data = {'query_id': self.query_id}

        # Insert to the queue table
        for self.handles in self.scraper.scrap_followers():
            for handle in self.handles:
                print(handle)
                acceptable_handle = handle_regex.findall(handle)
                if acceptable_handle:
                    data['user_handle'] = acceptable_handle[0]
                    print(data)
                    try:
                        self.sql.dict_to_sql(data, 'queue')
                        if followers_handle:
                            print(followers_handle)
                            self.sql.dict_to_sql({'user_handle':followers_handle.lower(),'following_handle':data['user_handle'].lower()},'following')
                    except Exception as e:
                        print(e)

    # ----------------FOR USERNAME (USER_TABLE)-----------------

    def get_cleaned_tweet_dictionary(self, tweet):
        """Make sure the dictionary is acceptable to the db.

        :param tweet:
        :return:

        """
        try:
            tweet.text = str(tweet.text).encode('utf-8', 'ignore')[:280]
            tweet.hashtags = tweet.hashtags.encode('utf-8', 'ignore')[:280]
            tweet.mentions = tweet.mentions.encode('utf-8')[:280]
        except Exception as e:
            print(e)
        # TODO: No username from got sometimes
        tweet.actual_name = tweet.username.encode('utf-8')
        tweet.user_handle = "@{}".format((tweet.user_handle).lower())
        tweet.permalink = tweet.permalink.encode('utf-8')
        tweet.retweets_permalink = tweet.retweets_permalink.encode('utf-8')
        tweet.urls_contained = tweet.urls[:200].encode('utf-8')
        tweet.tweet_id = tweet.id
        tweet.user_id = tweet.author_id

        del tweet.author_id
        del tweet.formatted_date
        del tweet.username
        del tweet.urls
        del tweet.id

        return tweet.__dict__

    def parent_update_users_based_on_queue(self):
        """ Parent Function for inserting followers profiles.

        :return:
        """
        # Update the user table inside function
        user_queue = self.read_queue(insert_for='user')
        while user_queue:
            user_handles = []
            user_query_dict = defaultdict()

            for row in user_queue:
                user_handles.append(row['user_handle'])
                user_query_dict[row['user_handle']] = row['query_id']
            users_updated, users_failed = self.update_user(user_query_dict)
            print("users updated {}".format(len(users_updated)))
            print("users failed {}".format(users_failed))
            self.update_user_status_in_queue_and_update_log(users_updated, users_failed)
            user_queue = self.read_queue(insert_for='user')

    def read_queue(self, insert_for=None):
        """ Reads 100 items from queue for user or one item for tweet

        :return:
        """
        if insert_for == 'user':
            return self.sql.get_data(
                'SELECT user_handle,query_id FROM queue WHERE user_status=0 and query_id={} and attempts < 5'.format(
                    self.query_id))[
                   :100]
        if insert_for == 'tweet':
            if self.shard_number:
                query = """SELECT user_handle, query_id FROM queue WHERE
                            tweet_count=0 and tweet_status=0 and query_id={} and attempts < 5 and id%{}={}""".format(
                    self.query_id, SHARDS, self.shard_number)
            else:
                query = """SELECT user_handle, query_id FROM queue WHERE
                            tweet_count=0 and query_id={} and attempts < 5""".format(
                    self.query_id)
            return self.sql_fetch.get_one_row(query)

    def update_user_status_in_queue_and_update_log(self, users_updated, users_failed):
        """

        :return:
        """
        print(len(users_failed))
        print(len(users_updated))
        for updated_user in users_updated:
            query = 'UPDATE queue SET user_status = 1, attempts= attempts+1 WHERE \
                      user_handle="{}" AND query_id={}'.format(
                updated_user['user_handle'].decode(), updated_user['query_id'])
            self.sql.write_cursor.execute(query)
            self.insert_user_log(updated_user)
        for failed_user in users_failed:
            query = 'UPDATE queue SET attempts = attempts+1 WHERE \
                      user_handle="{}" AND query_id={}'.format(
                failed_user['user_handle'], failed_user['query_id'])
            self.sql.write_cursor.execute(query)

    def update_user(self, user_query_dict):
        """

        :param user_handles:
        :return:
        """
        updated_users = []
        failed_users = []
        user_handles = user_query_dict.keys()
        responses_iterator = self.scraper.yield_profile_requests(user_handles)
        for responses in responses_iterator:
            for response in responses:
                twitter_user_dictionary = {}
                if response and response.status_code == 200:
                    twitter_user_dictionary = self.scraper.get_profile_dictionary(response)
                    if twitter_user_dictionary:
                        try:
                            query_id = user_query_dict[twitter_user_dictionary['user_handle'].decode()]
                            twitter_user_dictionary['query_id'] = query_id
                            if len(twitter_user_dictionary['profile_image_url'])>200:
                                twitter_user_dictionary['profile_image_url']=''
                            self.sql.dict_to_sql(twitter_user_dictionary, 'user')
                            updated_users.append(twitter_user_dictionary)

                        except Exception as e:
                            print('Exception1: {}'.format(e))
                            print(response.request.url)
                if not twitter_user_dictionary:
                    try:
                        user_handle = parse.unquote(response.request.url.split('/')[-1])
                        if user_handle == 'suspended':
                            user_handle = parse.unquote(response.history[0].url.split('/')[-1])
                        user_handle = user_handle.lower()
                        user_handle = user_handle.strip('?')
                        twitter_user_dictionary = {'user_handle': user_handle}
                        query_id = user_query_dict[user_handle]
                        twitter_user_dictionary['query_id'] = query_id
                        failed_users.append(twitter_user_dictionary)
                    except Exception as e:
                        print('Exception2: {}'.format(e))
                        if response:
                            print(response.request.url)
        return updated_users, failed_users

    def insert_user_log(self, user):
        """

        :param user:
        :return:
        """
        d = {'user_handle': user['user_handle'], 'query_id': user['query_id']}
        self.sql.dict_to_sql(d, 'user_query_log')

    # ---------------------FOR USERNAME (TWEET_TABLE--------------------)

    def update_tweet_based_on_queue(self):
        """ Parent Function for inserting followers tweets.

        :return:
        """
        row = self.read_queue(insert_for='tweet')
        while row is not None:
            # Get since/until from query table.
            self.query_id = row['query_id']
            # get parameters from query
            q = 'SELECT since,until FROM query WHERE query_id={}'.format(row["query_id"])
            self.sql.cursor.execute(q)
            query = self.sql.cursor.fetchone()  # Will return one record ideally
            self.update_tweets_from_usernames(user_handle=row['user_handle'],
                                           start_date=query['since'].strftime('%Y-%m-%d'),
                                           end_date=query['until'].strftime('%Y-%m-%d'), max_num=1000)
            self.update_tweet_status_in_queue_and_update_log(row['user_handle'])
            row = self.read_queue(insert_for='tweet')

    def update_tweets_from_usernames(self, user_handle=None, start_date=None, end_date=None, max_num=None):
        # start_date="2017-01-01"
        # end_date="2018-01-01"
        # usernames=joblib.load('/home/analytics/analytics/data/username.txt')
        if start_date is None:
            start_date = "2017-01-01"
        if end_date is None:
            end_date = "2018-01-01"

        tweetCriteria = gotmanager.TweetCriteria()
        tweetCriteria.include_retweets = self.include_retweets
        tweetCriteria.include_replies = self.include_replies
        tweetCriteria.setUsername('@' + user_handle.strip('@')).setSince(start_date).setUntil(
            end_date).setMaxTweets(max_num)
        # print(tweetCriteria.__dict__)
        tweets = gotmanager.TweetManager.getTweets(tweetCriteria)

        print("User Handle: {}, Tweets: {}".format(user_handle, len(tweets)))
        for tweet in tweets:
            # print(tweet)
            try:
                data = self.get_cleaned_tweet_dictionary(tweet)
                self.sql.dict_to_sql(data, 'tweet')
            except UnicodeEncodeError as e:
                print(tweet.__dict__)
                raise e

    def update_tweet_status_in_queue_and_update_log(self, handle):
        """

        :param handle:
        :return:
        """
        count_query = """select count(*) from tweet where user_handle='{}'""".format(handle)
        tweet_count = self.sql.get_data(count_query)[0]['count(*)']
        query = "UPDATE queue SET tweet_status = 1, attempts= attempts+1, tweet_count={} WHERE \
        user_handle='{}' AND query_id={}".format(tweet_count, handle, self.query_id)
        self.sql.write_cursor.execute(query)
        self.insert_tweet_log(handle)

        # TODO: If there isparent_update_tweets_based_on_query an error in extracting the tweets we must run the
        # TODO: code below
        # query = "UPDATE queue SET attempts= attempts+1 WHERE \
        #        user_handle='{}' AND query_id={}".format(handle, self.query_id)
        # self.sql.write_cursor.execute(query)

    def insert_tweet_log(self, handle):
        """

        :return:
        """
        # TODO: get tweet id from got_username.
        rows_tweet = self.sql.get_data("SELECT tweet_id, user_handle FROM tweet WHERE user_handle ='{}'".format(handle))
        for row in rows_tweet:
            self.sql.dict_to_sql({'tweet_id': row['tweet_id'], 'query_id': self.query_id, 'user_handle': row['user_handle']}, 'tweet_query_log')

    # -----------------FOR KEYWORDS (TWEET_TABLE)-----------------

    def parent_update_tweets_based_on_query(self):
        """ Parent function for getting tweets from query

        :return:
        """
        print("Hello from run_tweet_from_query")
        # try:
        #     self.insert_query()
        # except Exception as e:
        #     pass
        rows_query = self.sql.get_data('SELECT * FROM query WHERE query_id = {}'.format(self.query_id))
        for row in rows_query:
            print(row['entity'])
            print(type(row['since']))
            self.get_tweets_from_keyword_via_got(query=row['entity'], start_date=row['since'].strftime('%Y-%m-%d'),
                                                 end_date=row['until'].strftime('%Y-%m-%d'), max_num=10000)

    def got_wrapper_from_query(self, query=None, start_date=None, end_date=None, max_num=None):
        if start_date is None:
            start_date = "2017-01-01"
        if end_date is None:
            end_date = "2018-01-01"
        # usernames=joblib.load('/home/analytics/analytics/data/username.txt')
        print(start_date)
        print(type(start_date))
        print('----------------------------------------------------------------')
        tweet_criteria = gotmanager.TweetCriteria().setQuerySearch(query).setSince(start_date).setUntil(
            end_date).setMaxTweets(max_num)
        tweet_criteria.include_retweets = self.include_retweets
        tweet_criteria.include_replies =self.include_replies
        print("Inside got_wrapper_from_query in Twitter_loader")
        return gotmanager.TweetManager.getTweets(tweet_criteria)

    def get_tweets_from_keyword_via_got(self, query, start_date, end_date, max_num):
        """
        :param query:
        :param start_date:
        :param end_date:
        :param max_num:
        :return:
        """
        tweets = self.got_wrapper_from_query(query, start_date, end_date, max_num)
        for tweet in tweets:
            print("Hello from got_query")
            # print(get_cleaned_tweet_dictionary(tweet))
            self.sql.dict_to_sql(self.get_cleaned_tweet_dictionary(tweet), 'tweet')
            # inserting to tweet query log
            self.sql.dict_to_sql({'tweet_id': tweet.tweet_id, 'query_id': self.query_id ,'user_handle' : tweet.user_handle}, 'tweet_query_log')

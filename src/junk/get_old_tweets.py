import os
import time
import joblib

#home = os.path.abspath(os.path.dirname(__file__))
home = '/home/stealth/Devel/analytics/'
from lib.GetOldTweets.got3 import manager as gotmanager
from src.scraping.got_patch import getJsonReponse, getTweets
from src.mysql_utils import MySqlUtils
from datetime import datetime, timedelta
import sys
import re
import pandas as pd

# sys.path.append('/home/shubham/devel/analytics/')
# newfile_name = os.path.join( directory , "newfile.blend")


# Monkey Patching for a bug in GOT Library
gotmanager.TweetManager.getJsonReponse = getJsonReponse
gotmanager.TweetManager.getTweets = getTweets

end_date = datetime.now()
start_date = datetime.now() - timedelta(days=7)
start_date_string = '{}-{}-{}'.format(start_date.year, start_date.month, start_date.day)
end_date_string = '{}-{}-{}'.format(end_date.year, end_date.month, end_date.day)
NUM_TWEETS = 1000


def get_cleaned_tweet_dictionary(tweet):
    """Make sure the dictionary is acceptable to the db.

    :param tweet:
    :return:

    """
    print(tweet.__dict__)
    try:
        tweet.text = str(tweet.text).encode('utf-8', 'ignore')[:280]
        tweet.hashtags = tweet.hashtags.encode('utf-8', 'ignore')[:280]
        tweet.mentions = tweet.mentions.encode('utf-8')
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


def got_username(user_handle=None, start_date=None, end_date=None, max_num=None, include_retweets=None, include_replies=False):

    if start_date is None:
        start_date="2017-01-01"
    if end_date is None:
        end_date="2018-01-01"
    #usernames=joblib.load('/home/analytics/analytics/data/username.txt')
    print(start_date)
    for name in user_handle:
        print (name)
        print ('----------------------------------------------------------------')
        tweetCriteria = gotmanager.TweetCriteria()
        tweetCriteria.setUsername('@'+name.strip('@')).setSince(start_date).setUntil(
            end_date).setMaxTweets(max_num)
        tweetCriteria.include_retweets = include_retweets
        tweetCriteria.include_replies = include_replies

        tweets = gotmanager.TweetManager.getTweets(tweetCriteria)
        print (len(tweets))
        sql = MySqlUtils()
        tweet_dicts = []
        for tweet in tweets:
            #print (tweet)
            print(tweet.__dict__)
            tweet_dict = get_cleaned_tweet_dictionary(tweet)
            try:
                tweet_dicts.append(tweet_dict)
                sql.dict_to_sql(tweet_dict, 'tweet')
            except UnicodeEncodeError as e:
                print(tweet_dict)
                raise e
        data = pd.DataFrame(tweet_dicts)
        #data.to_csv(name+'.csv')


def got_wrapper_from_users(user_handle=None, start_date=None, end_date=None, max_num=None, include_retweets=None):
    # start_date="2017-01-01"
    # end_date="2018-01-01"
    #usernames=joblib.load('/home/analytics/analytics/data/username.txt'

    if start_date is None:
        start_date = "2017-01-01"
    if end_date is None:
        end_date = "2018-01-01"
    print(start_date)
    print(end_date)
    print (user_handle)
    print (include_retweets)
    print ('----------------------------------------------------------------')
    tweetCriteria = gotmanager.TweetCriteria()
    print(include_retweets)
    tweetCriteria.include_retweets = include_retweets
    tweetCriteria.setUsername('@'+user_handle.strip('@')).setSince(start_date).setUntil(
        end_date).setMaxTweets(max_num)
    print(tweetCriteria.__dict__)
    print ("Inside got_wrapper_from_user in Twitter_loader")
    return gotmanager.TweetManager.getTweets(tweetCriteria)

def got_wrapper_from_query(query=None,start_date=None, end_date=None, max_num=None, ):
    if start_date is None:
        start_date="2017-01-01"
    if end_date is None:
        end_date="2018-01-01"
    #usernames=joblib.load('/home/analytics/analytics/data/username.txt')
    print(start_date)
    print(type(start_date))
    print ('----------------------------------------------------------------')
    tweet_criteria = gotmanager.TweetCriteria().setQuerySearch(query).setSince(start_date).setUntil(
            end_date).setMaxTweets(max_num)
    print ("Inside got_wrapper_from_query in Twitter_loader")
    return gotmanager.TweetManager.getTweets(tweet_criteria)


def got_query(query, start_date, end_date, max_num):
    # Wrapper for get old tweets

    #:param start_date:
    #:param end_date:
    #:return:
    print("{} {} {} {}".format(query, start_date, end_date, max_num))
    tweetCriteria = gotmanager.TweetCriteria().setQuerySearch(query).setSince(start_date).setUntil(
        end_date).setMaxTweets(max_num)
    tweets = gotmanager.TweetManager.getTweets(tweetCriteria)
    sql = MySqlUtils()
    for tweet in tweets:
        tweet.query = query
        # print(tweet.__dict__)
        sql.dict_to_sql(get_cleaned_tweet_dictionary(tweet), 'tweet')


def get_old_tweets(start_date=start_date_string, end_date=end_date_string, max_num=NUM_TWEETS):
    # Wrapper for get old tweets

    #:param start_date:
    #:param end_date:
    #:return:

    with open(home + 'data/twitter_search_terms.txt') as f:
        search_list = f.read().splitlines()

    # query = ' OR '.join(search_list)
    for query in search_list:
        tweetCriteria = gotmanager.TweetCriteria().setQuerySearch(query).setSince(start_date).setUntil(
            end_date).setMaxTweets(max_num)
        tweets = gotmanager.TweetManager.getTweets(tweetCriteria)
        # sql = MySqlUtils()
        for tweet in tweets:
            tweet.query = query
            # print(tweet.__dict__)
            # sql.dict_to_sql(get_cleaned_tweet_dictionary(tweet), 'tweet')


"""

# get tweets for past 2 months for a particular query.
start_date = datetime(2016, 10, 17)
for i in range(9):
    end_date = start_date + timedelta(days=7)
    start_date_string = '{}-{}-{}'.format(start_date.year, start_date.month, start_date.day)
    end_date_string = '{}-{}-{}'.format(end_date.year, end_date.month, end_date.day)
    print("{} to {}".format(start_date_string, end_date_string))
    get_old_tweets(start_date=start_date_string, end_date=end_date_string)
    start_date = end_date


"""

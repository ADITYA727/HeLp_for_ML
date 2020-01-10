"""
author :-> Deepak
obj    :-> scrape the twitter user profile and store into the database.
input  :-> query_id
output :-> store user profile into database and user_status into queue table

"""
import os, getopt
import sys

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.scraping.twitter_loader import TwitterLoader
from src.mysql_utils import MySqlUtils

sql = MySqlUtils()


def main(argv):
    domain = ''
    source_type = ''
    entity = ''
    include_retweets = False
    shard_number = None

    opts, args = getopt.getopt(argv, "", (
        "entity=", "source_type=", "domain=", "include-retweets", "shard-number="))

    for opt, arg in opts:
        if opt == '--entity':
            entity = arg

        elif opt == '--source_type':
            source_type = arg

        elif opt == '--domain':
            domain = arg
        elif opt == '--include-retweets':
            include_retweets = True
        elif opt == '--shard-number':
            shard_number = arg

    if domain and source_type and entity:
        data_db = sql.get_data(
            "SELECT query_id FROM query WHERE domain = '{}' and source_type = '{}' and entity = '{}'".format(domain,
                                                                                                             source_type,
                                                                                                             entity))

    elif domain and source_type:
        data_db = sql.get_data(
            "SELECT query_id FROM query WHERE domain = '{}' and source_type = '{}'".format(domain, source_type))

    elif domain and entity:
        data_db = sql.get_data(
            "SELECT query_id FROM query WHERE domain = '{}' and entity = '{}'".format(domain, entity))

    elif domain:
        data_db = sql.get_data("SELECT query_id FROM query WHERE domain = '{}'".format(domain))

    elif entity:
        data_db = sql.get_data("SELECT query_id FROM query WHERE entity = '{}'".format(entity))

    elif source_type:
        data_db = sql.get_data("SELECT query_id FROM query WHERE source_type = '{}'".format(source_type))

    else:
        data_db = sql.get_data("SELECT query_id FROM query")

    for data in data_db:
        loader = TwitterLoader()
        loader.query_id = data['query_id']
        loader.include_retweets = include_retweets
        loader.shard_number = shard_number
        print("Getting Tweets for query_id: {}".format(data['query_id']))
        # read users from the queue based on query id and update the tweet in tweet table
        # and tweet status in queue table
        loader.update_tweet_based_on_queue()
        loader.close()


def print_error():
    """

    :return:
    """
    print(
        "python load_tweets_from_queue.py --source_type <source_type>"
        "--entity <entity> --domain <domain> --include_retweets"
    )


if __name__ == '__main__':
    main(sys.argv[1:])

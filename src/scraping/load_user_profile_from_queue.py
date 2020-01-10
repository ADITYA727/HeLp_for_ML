"""
author :-> Deepak
obj    :-> scrape the twitter user profile and store into the database.

input  :-> domain
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

    options = ("entity=", "source_type=", "domain=")
    try:
        opts, args = getopt.getopt(argv, "", options)
    except getopt.GetoptError:
        print("Incorrect Parameters \nUsage:")
        print_error()
        sys.exit()

    if not opts:
        print("Missing Parameters \nUsage:")
        print_error()
        sys.exit()

    opts, args = getopt.getopt(argv, "", options)

    for opt, arg in opts:
        if opt == '--entity':
            entity = arg

        elif opt == '--source_type':
            source_type = arg

        elif opt == '--domain':
            domain = arg

    if domain and source_type and entity:
        data_db = sql.get_data(
            "SELECT query_id FROM query WHERE domain = '{}' and source_type = '{}' and entity = '{}'".format(
                domain, source_type, entity))

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
        s = TwitterLoader(data)
        s.query_id = data['query_id']
        print(data['query_id'])
        # read users from the queue based on query id and update the user profile in user table
        # and user status in queue table
        s.parent_update_users_based_on_queue()
        s.close()


def print_error():
    """

    :return:
    """
    print(
        "python load_user_profile_from_queue.py --source_type <source_type>"
        " --entity <entity> --domain <domain>"
    )


if __name__ == '__main__':
    main(sys.argv[1:])

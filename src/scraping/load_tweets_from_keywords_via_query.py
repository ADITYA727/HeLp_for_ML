"""
 author :- Deepak
 obj    :- to insert the tweets into the database based on the keywords
 input  :- data dictionary which is a input to the query table
 output :- insert into the tweet and tweet_query_log table

"""
import os,getopt
import sys
home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.scraping.twitter_loader import TwitterLoader
from src.mysql_utils import MySqlUtils


sql = MySqlUtils()
def main(argv):
    data = {}
    options = ("entity=", "source_type=", "domain=", "since=", "until=", "location=")
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

    for opt, arg in opts:
        if opt == '--entity':
            data['entity'] = arg

        elif opt == '--source_type':
            data['source_type'] = arg

        elif opt == '--domain':
            data['domain'] = arg

        elif opt == '--since':
            data['since']= arg

        elif opt == '--until':
            data['until'] = arg

        elif opt == '--location':
            data['until'] = arg
    domain = data['domain']
    data_db = sql.get_data("SELECT * FROM query WHERE domain = '{}'".forma(data['entity']))
    for data in data_db:
        s = TwitterLoader(data)
        s.query_id = data['query_id']
        print('query ====>', s.query_id)
        s.parent_update_tweets_based_on_query()
        s.close()

def print_error():
    """

    :return:
    """
    print(
        "python load_tweets_from_keywords_via_query.py --source_type <source_type>"
        "--entity <entity> --domain <domain> --include_retweets"
        "--location <location> --since <since> --until <until>"
    )

if __name__ == '__main__':
	main(sys.argv[1:])

"""
author    :- Deepak
objective :- To insert the query into database and add the users or
                followers based on query in queue table.
input     :- data which is a dicitonary
output    :- update the queue and query table in database

"""
import os, sys, getopt

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../..')
from src.scraping.twitter_loader import TwitterLoader


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
            data['since'] = arg

        elif opt == '--until':
            data['until'] = arg

        elif opt == '--location':
            data['location'] = arg

    s = TwitterLoader(data)
    s.insert_query()
    url='https://mobile.twitter.com/{}/followers'.format(data['entity'])
    s.insert_queue(url=url)

    s.close()

def print_error():
    """

    :return:
    """
    print(
        "python load-query_and_queue.py --source_type <source_type>"
        "--entity <entity> --domain <domain> --include_retweets"
        "--location <location> --since <since> --until <until>"
    )

if __name__ == '__main__':
    main(sys.argv[1:])

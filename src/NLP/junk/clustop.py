import os
import sys
import joblib
import re
import itertools
import numpy as np
import networkx as nx
import community

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query
from src.NLP.preprocessing import clean_tweet, stopwords, links, twitter_pic


def get_data(length=500000):
    sql = MySqlUtils()
    users = sql.get_data(user_query)
    users_list = [user['user_handle'] for user in users[:length]]
    print('Query count {}'.format(len(users)))
    query = 'SELECT text, user_handle, retweets, retweets_permalink FROM tweet where user_handle IN (' + ','.join(
        ("'{}'".format(user) for user in users_list)) + ')'

    tweets = sql.get_data(query)
    print("Tweets", len(tweets))
    return tweets


def cluster_tweets_based_on_hashtag():
    tweets = get_data(length=2000)
    hashtags = []
    tweets_hashtags = []

    for t in tweets:
        tweet = t['text']

        # pyquery cleaning
        corrections = [
            ('http:// ', 'http://'),
            ('https:// ', 'https://'),
            ('http://www. ', 'http://www.'),
            ('https://www. ', 'https://www.'),
            ('pic.twitter.com', 'https://pic.twitter.com'),
            ('# ', '#')
        ]
        for correction in corrections:
            tweet = tweet.replace(correction[0], correction[1])

        tweet = links.sub('', tweet)
        tweet = twitter_pic.sub('', tweet)

        tweet_hashtags = re.findall(r'#(\w+)', tweet)
        hashtags += tweet_hashtags
        if len(tweet_hashtags) > 0:
            tweets_hashtags.append(list(set(map(str.lower, tweet_hashtags))))

    hashtags = list(set(map(str.lower, hashtags)))
    joblib.dump(hashtags, 'clustop_hashtags.pkl')
    hashtags_dict = {}
    for ctr, h in enumerate(hashtags):
        hashtags_dict[h] = ctr
    hashtags_count = len(hashtags)

    co_occurence_matrix = np.zeros((hashtags_count, hashtags_count))

    for elem in tweets_hashtags:
        for combination in itertools.combinations(elem, 2):
            h1 = combination[0]
            h2 = combination[1]
            position1 = hashtags_dict[h1]
            position2 = hashtags_dict[h2]
            co_occurence_matrix[position1, position2] += 1
            co_occurence_matrix[position2, position1] += 1

    print(co_occurence_matrix.shape)
    G = nx.from_numpy_matrix(co_occurence_matrix)
    communities = community.best_partition(G)
    print(communities)
    joblib.dump(communities, 'clustop_communities.pkl')


def get_communities():
    communities = {}
    hashtags = joblib.load('clustop_hashtags.pkl')
    labels = joblib.load('clustop_labels.pkl')

    for hashtag_index, label in labels.items():
        hashtag = hashtags[hashtag_index]
        if label in communities:
            communities[label].append(hashtag)
        else:
            communities[label] = [hashtag]

    communities_len = {}
    for label, hashtags in communities.items():
        communities_len[label] = len(hashtags)

    ctr = 1
    for key in sorted(communities_len, key=communities_len.get, reverse=True)[:50]:
        print('Community ' + str(ctr))
        print(communities[key][:150])
        print('\n')
        ctr += 1


if __name__ == '__main__':
    get_communities()

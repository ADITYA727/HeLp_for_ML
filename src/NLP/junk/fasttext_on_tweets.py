import os
import sys
import numpy as np
from pprint import pprint

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query
from src.NLP.preprocessing import clean_tweet
from sklearn.cluster import KMeans


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


def train_fasttext():
    f = open('fasttext_train.txt', 'w')
    tweets = get_data(length=1500)
    for tweet in tweets:
        f.write(clean_tweet(tweet['text']))
        f.write('\n')

    f.close()


def build_word_vectors():
    vectors = {}
    with open('fasttext_vectors.txt.vec') as f:
        for ctr,line in enumerate(f):
            if ctr > 0:
                vector = line.split(' ')
                word = vector[0]
                vectors[word] = list(map(float, vector[1:-1]))

    return vectors


def cluster_words():
    vectors = build_word_vectors()

    n_clusters = 30
    k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    nd_array = np.array(list(vectors.values()))
    k_means.fit(nd_array)

    words = list(vectors.keys())
    for i in range(n_clusters):
        print('Cluster %s' % i)
        distance_from_center = k_means.transform(nd_array)[:, i] # distance to the first cluster center and so on..
        nearest_points = np.argsort(distance_from_center)[::][:20]
        nearest_words = [words[point] for point in nearest_points]
        print(nearest_words)


if __name__ == '__main__':
    # train_fasttext()
    cluster_words()

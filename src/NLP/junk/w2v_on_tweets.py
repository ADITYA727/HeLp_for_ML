import os
import sys
import joblib
import numpy as np
from pprint import pprint

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query
from src.NLP.preprocessing import clean_tweet, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from gensim.models import Word2Vec
import gensim


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


def run_w2v():
    tweets = get_data(length=1500)
    clean_tweets = [clean_tweet(tweet['text'], as_string=False) for tweet in tweets]
    #bigram_transformer = gensim.models.Phrases(clean_tweets)
    model = Word2Vec(sentences=clean_tweets, sg=1, size=200, window=5, min_count=10)
    return model


def cluster_words():
    model = run_w2v()
    vectors = {}
    for word in model.wv.vocab:
        vectors[word] = model[word]

    joblib.dump(vectors, 'w2v_word_vectors.pkl')

    # n_clusters = 100
    # k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    # nd_array = np.array(list(vectors.values()))
    # k_means.fit(nd_array)
    # labels = list(k_means.labels_)

    # words = list(vectors.keys())
    # for i in range(n_clusters):
    #     print('Cluster %s' % i)
    #     distance_from_center = k_means.transform(nd_array)[:, i] # distance to the first cluster center and so on..
    #     nearest_points = np.argsort(distance_from_center)[::][:15]
    #     nearest_words = [words[point] for point in nearest_points]
    #     print(nearest_words)
    #     print(labels.count(i))
    #     print('\n')


def cluster_tweets():
    word_vectors = joblib.load('w2v_word_vectors.pkl')

    tweets = get_data(length=2000)
    # vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, max_df=0.02, preprocessor=clean_tweet)
    # vectorizer.fit([t['text'] for t in tweets])
    # features = vectorizer.get_feature_names()

    clean_tweets = list(filter(None, [clean_tweet(t['text']) for t in tweets]))
    print(len(clean_tweets))
    tweet_vectors = {}
    for tweet in clean_tweets:
        tweet_word_vectors = []
        # tf_idf_vector = vectorizer.transform([tweet]).todense().tolist()[0]
        tweet_words = tweet.split()
        for word in tweet_words:
            if word in word_vectors:
                word_vector = word_vectors[word]
                # try:
                #     tf_idf_score = tf_idf_vector[features.index(word)]
                # except ValueError:
                #     tf_idf_score = 0
                # word_vector *= tf_idf_score
                tweet_word_vectors.append(list(word_vector))

        if len(tweet_word_vectors) > 0:
            tweet_vector = np.array(tweet_word_vectors).mean(axis=0)
            tweet_vectors[tweet] = tweet_vector

    tweet_vectors_values = list(tweet_vectors.values())
    final_tweets = list(tweet_vectors.keys())

    n_clusters = 30
    k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    k_means.fit(tweet_vectors_values)
    labels = list(k_means.labels_)

    for i in range(n_clusters):
        print('Cluster %s' % i)
        distance_from_center = k_means.transform(tweet_vectors_values)[:, i] # distance to the first cluster center and so on..
        nearest_points = np.argsort(distance_from_center)[::][:100]
        nearest_tweets = [final_tweets[point] for point in nearest_points]

        vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, min_df=3, preprocessor=clean_tweet)
        vector_matrix = vectorizer.fit_transform(nearest_tweets)
        tf_idf_words = np.array(vectorizer.get_feature_names())
        tf_idf_sorting = np.argsort(vector_matrix.toarray()).flatten()[::-1]
        top_words = tf_idf_words[tf_idf_sorting][:20]

        print(labels.count(i))
        print(nearest_tweets)
        print(top_words)
        print('\n')


def visualize_clusters():
    """
    http://www.dummies.com/programming/big-data/data-science/how-to-visualize-the-clusters-in-a-k-means-unsupervised-learning-model/
    """

    print('1')
    word_vectors = joblib.load('w2v_word_vectors.pkl')
    print('2')

    tweets = get_data(length=2000)
    print('3')

    clean_tweets = list(filter(None, [clean_tweet(t['text']) for t in tweets]))
    print(len(clean_tweets))
    print('4')

    tweet_vectors = {}
    for tweet in clean_tweets:
        tweet_word_vectors = []
        tweet_words = tweet.split()
        for word in tweet_words:
            if word in word_vectors:
                word_vector = word_vectors[word]
                tweet_word_vectors.append(list(word_vector))

        if len(tweet_word_vectors) > 0:
            tweet_vector = np.array(tweet_word_vectors).mean(axis=0)
            tweet_vectors[tweet] = tweet_vector

    print('5')

    tweet_vectors_values = list(tweet_vectors.values())
    final_tweets = list(tweet_vectors.keys())

    print('6')

    pca = PCA(n_components=2).fit(tweet_vectors_values)
    pca_2d = pca.transform(tweet_vectors_values)

    print('7')

    n_clusters = 30
    k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    k_means.fit(tweet_vectors_values)

    plt.figure('K-means with 30 clusters')
    plt.scatter(pca_2d[:, 0], pca_2d[:, 1], c=k_means.labels_)
    plt.show()


if __name__ == '__main__':
    visualize_clusters()

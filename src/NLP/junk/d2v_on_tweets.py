import os
import sys
import joblib
import numpy as np

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query
from src.NLP.preprocessing import clean_tweet, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


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


def get_documents(tweets):
    tagged_documents = []
    for ctr, tweet in enumerate(tweets):
        tagged_documents.append(TaggedDocument(tweet, [ctr]))

    return tagged_documents


def run_d2v():
    tweets = get_data(length=2000)
    clean_tweets = list(filter(None, [clean_tweet(t['text'], as_string=False) for t in tweets]))
    print('Clean tweets:', len(clean_tweets))
    documents = get_documents(clean_tweets)
    model = Doc2Vec(documents=documents, dm=1, size=200, window=5, min_count=10)
    return (model, clean_tweets)


def cluster_tweets():
    # model, clean_tweets = run_d2v()
    # tweet_vectors = {}
    # for ctr, t in enumerate(clean_tweets):
    #     key = ' '.join(t)
    #     tweet_vectors[key] = model.docvecs[ctr]

    # joblib.dump(tweet_vectors, 'd2v_tweet_vectors.pkl')

    tweet_vectors = joblib.load('d2v_tweet_vectors.pkl')

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

        try:
            vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, min_df=3, preprocessor=clean_tweet)
            vector_matrix = vectorizer.fit_transform(nearest_tweets)
        except ValueError:
            vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, preprocessor=clean_tweet)
            vector_matrix = vectorizer.fit_transform(nearest_tweets)

        tf_idf_words = np.array(vectorizer.get_feature_names())
        tf_idf_sorting = np.argsort(vector_matrix.toarray()).flatten()[::-1]
        top_words = tf_idf_words[tf_idf_sorting][:20]

        print(labels.count(i))
        print(nearest_tweets)
        print(top_words)
        print('\n')


if __name__ == '__main__':
    cluster_tweets()

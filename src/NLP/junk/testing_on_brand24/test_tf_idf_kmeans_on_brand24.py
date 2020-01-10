import os
import sys
import gensim
import joblib
from gensim import corpora

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from src.NLP.preprocessing import clean_tweet, stopwords
from src.NLP.junk.testing_on_brand24.test_w2v_on_brand24 import get_b24_tweets, get_accuracy

Lda = gensim.models.ldamodel.LdaModel


def make_tf_idf_matrix():
    tweets = get_b24_tweets()
    vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, max_df=0.02, preprocessor=clean_tweet)
    vector_matrix = vectorizer.fit_transform([tweet for tweet in tweets])
    joblib.dump(vector_matrix, 'src/NLP/junk/testing_on_brand24/data/tf_idf_vector_matrix.pkl')


def cluster_tweets():
    all_tweets = get_b24_tweets()
    vector_matrix = joblib.load('src/NLP/junk/testing_on_brand24/data/tf_idf_vector_matrix.pkl')
    n_clusters = 10
    k_means = KMeans(n_clusters=n_clusters)
    k_means.fit(vector_matrix)
    labels = list(k_means.labels_)

    clusters = {}
    for ctr, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(all_tweets[ctr])
        else:
            clusters[label] = [all_tweets[ctr]]

    joblib.dump(clusters, 'src/NLP/junk/testing_on_brand24/data/tf_idf_kmeans_clusters.pkl')


if __name__ == '__main__':
    #make_tf_idf_matrix()
    cluster_tweets()
    get_accuracy('src/NLP/junk/testing_on_brand24/data/tf_idf_kmeans_clusters.pkl')

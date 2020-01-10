import os
import sys
import gensim
import joblib
from gensim import corpora

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from src.NLP.preprocessing import clean_tweet, stopwords
from src.NLP.junk.testing_on_brand24.test_w2v_on_brand24 import get_b24_tweets, get_accuracy

Lda = gensim.models.ldamodel.LdaModel


def cluster_tweets():
    all_tweets = get_b24_tweets()
    vector_matrix = joblib.load('src/NLP/junk/testing_on_brand24/data/tf_idf_vector_matrix.pkl')

    lsa = TruncatedSVD(n_components=200, algorithm='arpack')
    vector_lsa = lsa.fit_transform(vector_matrix)

    n_clusters = 10
    k_means = KMeans(n_clusters=n_clusters)
    k_means.fit(vector_lsa)
    labels = list(k_means.labels_)

    clusters = {}
    for ctr, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(all_tweets[ctr])
        else:
            clusters[label] = [all_tweets[ctr]]

    joblib.dump(clusters, 'src/NLP/junk/testing_on_brand24/data/tf_idf_lsi_kmeans_clusters.pkl')


if __name__ == '__main__':
    cluster_tweets()
    get_accuracy('src/NLP/junk/testing_on_brand24/data/tf_idf_lsi_kmeans_clusters.pkl')

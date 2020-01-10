import os
import sys
import gensim
import numpy as np
import joblib
from gensim import corpora
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query
from src.NLP.preprocessing import clean_tweet, stopwords
from sklearn.metrics import silhouette_score
from scipy import sparse
from sklearn.utils import check_X_y
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.cluster.unsupervised import check_number_of_labels
from numba import jit


@jit(nogil=True, parallel=True)
def euclidean_distances_numba(X, Y=None, Y_norm_squared=None):
    # disable checks
    XX_ = (X * X).sum(axis=1)
    XX = XX_.reshape((1, -1))

    if X is Y:  # shortcut in the common case euclidean_distances(X, X)
        YY = XX.T
    elif Y_norm_squared is not None:
        YY = Y_norm_squared
    else:
        YY_ = np.sum(Y * Y, axis=1)
        YY = YY_.reshape((1,-1))

    distances = np.dot(X, Y.T)
    distances *= -2
    distances += XX
    distances += YY
    distances = np.maximum(distances, 0)

    return np.sqrt(distances)


@jit(parallel=True)
def euclidean_distances_sum(X, Y=None):
    if Y is None:
        Y = X
    Y_norm_squared = (Y ** 2).sum(axis=1)
    sums = np.zeros((len(X)))
    for i in range(len(X)):
        base_row = X[i, :]
        sums[i] = euclidean_distances_numba(base_row.reshape(1, -1), Y, Y_norm_squared=Y_norm_squared).sum()

    return sums


@jit(parallel=True)
def euclidean_distances_mean(X, Y=None):
    if Y is None:
        Y = X
    Y_norm_squared = (Y ** 2).sum(axis=1)
    means = np.zeros((len(X)))
    for i in range(len(X)):
        base_row = X[i, :]
        means[i] = euclidean_distances_numba(base_row.reshape(1, -1), Y, Y_norm_squared=Y_norm_squared).mean()

    return means


def silhouette_samples_memory_saving(X, labels, metric='euclidean', **kwds):
    X, labels = check_X_y(X, labels, accept_sparse=['csc', 'csr'])
    le = LabelEncoder()
    labels = le.fit_transform(labels)
    check_number_of_labels(len(le.classes_), X.shape[0])

    unique_labels = le.classes_
    n_samples_per_label = np.bincount(labels, minlength=len(unique_labels))

    # For sample i, store the mean distance of the cluster to which
    # it belongs in intra_clust_dists[i]
    intra_clust_dists = np.zeros(X.shape[0], dtype=X.dtype)

    # For sample i, store the mean distance of the second closest
    # cluster in inter_clust_dists[i]
    inter_clust_dists = np.inf + intra_clust_dists

    for curr_label in range(len(unique_labels)):

        # Find inter_clust_dist for all samples belonging to the same label.
        mask = labels == curr_label

        # Leave out current sample.
        n_samples_curr_lab = n_samples_per_label[curr_label] - 1
        if n_samples_curr_lab != 0:
            intra_clust_dists[mask] = euclidean_distances_sum(X[mask, :]) / n_samples_curr_lab

        # Now iterate over all other labels, finding the mean
        # cluster distance that is closest to every sample.
        for other_label in range(len(unique_labels)):
            if other_label != curr_label:
                other_mask = labels == other_label
                other_distances = euclidean_distances_mean(X[mask, :], X[other_mask, :])
                inter_clust_dists[mask] = np.minimum(inter_clust_dists[mask], other_distances)

    sil_samples = inter_clust_dists - intra_clust_dists
    sil_samples /= np.maximum(intra_clust_dists, inter_clust_dists)
    # score 0 for clusters of size 1, according to the paper
    sil_samples[n_samples_per_label.take(labels) == 1] = 0
    return sil_samples


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


def cluster_tweets():
    tweets = get_data(length=2000)
    vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, max_df=0.02, preprocessor=clean_tweet)
    vector_matrix = vectorizer.fit_transform([tweet['text'] for tweet in tweets])

    lsa = TruncatedSVD(n_components=200, algorithm='arpack')
    vector_lsa = lsa.fit_transform(vector_matrix)

    ## Silhouette
    #n_clusters = 30
    # for n_cluster in range(2, 40):
    #     k_means = KMeans(n_clusters=n_cluster, init='k-means++', max_iter=100)
    #     k_means.fit(vector_lsa)
    #     label = k_means.labels_
    #     # vector_lsa = sparse.csr_matrix(vector_lsa)
    #     sil_coeff = np.mean(silhouette_samples_memory_saving(vector_lsa, label, metric='euclidean'))
    #     print(n_cluster, sil_coeff)
    #     #print("\n")
    #     #sil_coeff = silhouette_score(vector_lsa, label, metric='euclidean', sample_size=10000)
    #     #with open('silhoette_values.txt', 'a') as f:
    #         #f.write("For n_clusters={}, The Silhouette Coefficient is {}".format(n_cluster, sil_coeff) + "\n")

    n_clusters = 100
    k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    k_means.fit(vector_lsa)

    weights = np.dot(k_means.cluster_centers_, lsa.components_)
    features = vectorizer.get_feature_names()
    weights = np.abs(weights)
    labels = list(k_means.labels_)

    for i in range(k_means.n_clusters):
        top = np.argsort(weights[i])[-15:]
        print(labels.count(i))
        print([features[j] for j in top])
        print('\n')

    joblib.dump(vectorizer, 'vectorizer_2.pkl')
    joblib.dump(weights, 'weights_2.pkl')


if __name__ == '__main__':
    cluster_tweets()

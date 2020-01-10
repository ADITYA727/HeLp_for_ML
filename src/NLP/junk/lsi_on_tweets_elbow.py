import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
from scipy.spatial.distance import cdist, pdist


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
    tweets = get_data(length=1500)
    vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, max_df=0.02, preprocessor=clean_tweet)
    vector_matrix = vectorizer.fit_transform([tweet['text'] for tweet in tweets])

    lsa = TruncatedSVD(n_components=200, algorithm='arpack')
    vector_lsa = lsa.fit_transform(vector_matrix)

    K = range(1,50)
    KM = [KMeans(n_clusters=k).fit(vector_lsa) for k in K]
    centroids = [k.cluster_centers_ for k in KM]

    D_k = [cdist(vector_lsa, cent, 'euclidean') for cent in centroids]
    cIdx = [np.argmin(D,axis=1) for D in D_k]
    dist = [np.min(D,axis=1) for D in D_k]
    avgWithinSS = [sum(d)/vector_lsa.shape[0] for d in dist]

    # Total with-in sum of square
    wcss = [sum(d**2) for d in dist]
    tss = sum(pdist(vector_lsa)**2)/vector_lsa.shape[0]
    bss = tss-wcss

    kIdx = 10-1

    # elbow curve
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(K, avgWithinSS, 'b*-')
    ax.plot(K[kIdx], avgWithinSS[kIdx], marker='o', markersize=12, 
    markeredgewidth=2, markeredgecolor='r', markerfacecolor='None')
    plt.grid(True)
    plt.xlabel('Number of clusters')
    plt.ylabel('Average within-cluster sum of squares')
    plt.title('Elbow for KMeans clustering')
    plt.savefig('elbow_sum_squares.png')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(K, bss/tss*100, 'b*-')
    plt.grid(True)
    plt.xlabel('Number of clusters')
    plt.ylabel('Percentage of variance explained')
    plt.title('Elbow for KMeans clustering')
    plt.savefig('elbow_variance.png')


    # wcss = []
    # for i in range(2,40):
    #     kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
    #     kmeans.fit(vector_lsa)
    #     wcss.append(kmeans.inertia_)
     
    # plt.plot(range(2,40), wcss)
    # plt.title("The elbow method")
    # plt.xlabel("The number of clusters")
    # plt.ylabel("WCSS")
    # plt.savefig("elbow_method.png")

if __name__ == '__main__':
    cluster_tweets()

import os
import sys
import random
import numpy as np
import joblib
import itertools
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering
from gensim.models import Word2Vec
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')
from src.NLP.preprocessing import clean_tweet, stopwords
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query


categories = [
    'bollywood','politics', 'cricket', 'bigg_boss', 'football', 'machine_learning', 'happy_birthday',
    'hollywood', 'mobiles', 'food'
]

categories_words_removal = {
    'bollywood': ['#bollywood'],
    'politics': ['@narendramodi', '@amitshah'],
    'cricket': ['#indiavssouthafrica', '#SAvsIND', '#indvsa', '#teamindia', '#indvssl', '#slvsind'],
    'bigg_boss': ['bigg boss', 'bb11'],
    'football': ['#fcbarcelona', '#chelsea'],
    'machine_learning': ['#machinelearning', '#bigdata'],
    'happy_birthday': [],
    'hollywood': ['#hollywood'],
    'mobiles': ['redmi note'],
    'food': ['pasta'],
}

def remove_duplicates():
    """
    Remove those tweets which are present in more than 1 categories.
    """
    for category in categories:
        category_data = joblib.load('data/brand24/%s_tweets.pkl' % (category,))
        unique = []
        for d in category_data:
            if b24_all_tweets.count(d['content']) == 1:
                unique.append(d)
        joblib.dump(unique, 'data/brand24/%s_tweets.pkl' % (category,))


def remove_false_football_tweets():
    football_tweets = joblib.load('data/brand24/football_tweets.pkl')
    correct_tweets = []
    for d in football_tweets:
        if not '#liverpool' in d['content'].lower():
            correct_tweets.append(d)
    joblib.dump(correct_tweets, 'data/brand24/football_tweets.pkl')


def clean_b24_tweet(tweet, category):
    tweet = tweet.lower()
    words_to_remove = categories_words_removal[category]
    for w in words_to_remove:
        tweet = tweet.replace(w.lower(), '')

    return tweet


def build_data():
    b24_tweets_labeled = {}

    for category in categories:
        tweets = joblib.load('data/brand24/%s_tweets.pkl' % category)
        b24_tweets_labeled[category] = [tweet['content'] for tweet in tweets]

    joblib.dump(b24_tweets_labeled, 'src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')


def get_b24_tweets():
    b24_tweets_labeled = joblib.load('src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')
    tweets_lists = list(b24_tweets_labeled.values())
    b24_all_tweets = list(itertools.chain.from_iterable(tweets_lists))
    print('B24 tweets', len(b24_all_tweets))
    return b24_all_tweets


def get_b24_tweets_sample():
    b24_tweets_labeled = joblib.load('src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')
    tweets_lists = list(b24_tweets_labeled.values())
    tweets_lists_random = [random.sample(l, int(0.25*len(l))) for l in tweets_lists]
    b24_all_tweets = list(itertools.chain.from_iterable(tweets_lists_random))
    print('B24 tweets', len(b24_all_tweets))
    return b24_all_tweets


def get_db_tweets(length=500000):
    sql = MySqlUtils()
    users = sql.get_data(user_query)
    users_list = [user['user_handle'] for user in users[:length]]
    print('Query count {}'.format(len(users)))
    query = 'SELECT text FROM tweet where user_handle IN (' + ','.join(
        ("'{}'".format(user) for user in users_list)) + ')'

    tweets = sql.get_data(query)
    print('DB tweets', len(tweets))
    return tweets


def train_w2v():
    b24_all_tweets = get_b24_tweets()
    db_tweets = [t['text'] for t in get_db_tweets(length=2000)]
    all_tweets = b24_all_tweets + db_tweets
    clean_tweets = [clean_tweet(t, as_string=False) for t in all_tweets]
    model = Word2Vec(sentences=clean_tweets, sg=1, size=200, window=10, min_count=10)
    word_vectors = {}
    for word in model.wv.vocab:
        word_vectors[word] = model[word]

    joblib.dump(model, 'src/NLP/junk/testing_on_brand24/data/model.pkl')
    joblib.dump(word_vectors, 'src/NLP/junk/testing_on_brand24/data/word_vectors.pkl')


def cluster_tweets():
    word_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/word_vectors.pkl')
    all_tweets = get_b24_tweets_sample()
    tweets_categories = get_tweets_categories()

    tweet_vectors = {}
    for t in all_tweets:
        tweet_category = tweets_categories[t]
        tweet_word_vectors = []
        tweet_words = clean_tweet(clean_b24_tweet(t, tweet_category)).split()
        for word in tweet_words:
            if word in word_vectors:
                word_vector = word_vectors[word]
                tweet_word_vectors.append(list(word_vector))

        if len(tweet_word_vectors) > 0:
            tweet_vector = np.array(tweet_word_vectors).mean(axis=0)
            tweet_vectors[t] = tweet_vector

    joblib.dump(tweet_vectors, 'src/NLP/junk/testing_on_brand24/data/tweet_vectors.pkl')

    # tweet_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/tweet_vectors.pkl')
    tweet_vectors_values = list(tweet_vectors.values())
    # b24_tweets_labeled = joblib.load('src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')
    # centroids = []
    # for category, tweets in b24_tweets_labeled.items():
    #     category_tweet_vectors = []
    #     for t in tweets:
    #         try:
    #             category_tweet_vectors.append(list(tweet_vectors[t]))
    #         except Exception as e:
    #             pass

    #     category_centroid = np.array(category_tweet_vectors).mean(axis=0)
    #     centroids.append(category_centroid)

    # centroids_array = np.array(centroids)
    # pca = PCA(n_components=2).fit(tweet_vectors_values)
    # pca_2d = pca.transform(tweet_vectors_values)
    # joblib.dump(pca_2d, 'src/NLP/junk/testing_on_brand24/data/pca_2d.pkl')

    n_clusters = 10
    spectral = SpectralClustering(n_clusters=n_clusters)
    spectral.fit(tweet_vectors_values)
    labels = list(spectral.labels_)

    clusters = {}
    for ctr, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(all_tweets[ctr])
        else:
            clusters[label] = [all_tweets[ctr]]

    joblib.dump(clusters, 'src/NLP/junk/testing_on_brand24/data/clusters.pkl')


def get_tweets_categories():
    tweets_categories = {}
    b24_tweets_labeled = joblib.load('src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')
    for category, tweets_list in b24_tweets_labeled.items():
        for t in tweets_list:
            tweets_categories[t] = category

    return tweets_categories


def get_accuracy(clusters_pkl):
    tweet_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/tweet_vectors.pkl')
    tweets_categories = get_tweets_categories()
    clusters = joblib.load(clusters_pkl)
    predicted_clusters = {}
    for category in categories:
        predicted_clusters[category] = []

    ctr = 1
    correct_count = 0
    for label, tweets in clusters.items():
        actual_categories = []
        for t in tweets:
            actual_category = tweets_categories[t]
            actual_categories.append(actual_category)
        print('Cluster ', str(ctr))
        print(Counter(actual_categories))
        accuracy_percent = int((Counter(actual_categories).most_common(1)[0][1]/len(tweets)) * 100)
        print('Cluster length: ', len(tweets))
        print('Accuracy: {}%'.format(accuracy_percent))
        category = Counter(actual_categories).most_common(1)[0][0]
        predicted_clusters[category].append('{}%'.format(accuracy_percent))
        print('\n')
        correct_count += Counter(actual_categories).most_common(1)[0][1]
        ctr += 1

    print('*'*50 + '\n')

    for category, accuracies in predicted_clusters.items():
        print(category)
        print('Clusters: %s' % len(accuracies))
        if len(accuracies) > 0:
            print('Accuracies: %s' % ', '.join(accuracies))
        print('\n')

    overall_accuracy_percent = round((correct_count/len(tweet_vectors)) * 100, 2)

    print('*'*50 + '\n')
    print('Overall accuracy: {}%'.format(overall_accuracy_percent))


def visualize_clusters():
    # word_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/word_vectors.pkl')
    all_tweets = get_b24_tweets()

    # tweet_vectors = {}
    # for t in all_tweets:
    #     tweet_word_vectors = []
    #     tweet_words = clean_tweet(t).split()
    #     for word in tweet_words:
    #         if word in word_vectors:
    #             word_vector = word_vectors[word]
    #             tweet_word_vectors.append(list(word_vector))

    #     if len(tweet_word_vectors) > 0:
    #         tweet_vector = np.array(tweet_word_vectors).mean(axis=0)
    #         tweet_vectors[t] = tweet_vector

    # joblib.dump(tweet_vectors, 'src/NLP/junk/testing_on_brand24/data/tweet_vectors.pkl')

    # tweet_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/tweet_vectors.pkl')
    # tweet_vectors_values = list(tweet_vectors.values())

    # pca = PCA(n_components=2).fit(tweet_vectors_values)
    # pca_2d = pca.transform(tweet_vectors_values)

    # joblib.dump(pca_2d, 'src/NLP/junk/testing_on_brand24/data/pca_2d.pkl')

    # n_clusters = 10
    # k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    # k_means.fit(tweet_vectors_values)

    # joblib.dump(k_means, 'src/NLP/junk/testing_on_brand24/data/k_means.pkl')
    # k_means = joblib.load('src/NLP/junk/testing_on_brand24/data/k_means.pkl')
    # pca_2d = joblib.load('src/NLP/junk/testing_on_brand24/data/pca_2d.pkl')

    # indices = []
    # for ctr,label in enumerate(k_means.labels_):
    #     if label == 4:
    #         indices.append(ctr)

    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # ax.set_xlim([-3, 4])
    # ax.set_ylim([-3, 4])
    # plt.scatter(pca_2d[indices, 0], pca_2d[indices, 1])
    # plt.show()

    # k_means = joblib.load('src/NLP/junk/testing_on_brand24/data/k_means.pkl')
    # clusters = {}
    # for ctr, label in enumerate(k_means.labels_):
    #     if label in clusters:
    #         clusters[label].append(all_tweets[ctr])
    #     else:
    #         clusters[label] = [all_tweets[ctr]]

    # joblib.dump(clusters, 'src/NLP/junk/testing_on_brand24/data/clusters.pkl')

    b24_tweets_labeled = joblib.load('src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')
    tweet_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/tweet_vectors.pkl')
    tweet_vectors_values = list(tweet_vectors.values())
    tweet_vectors_keys = list(tweet_vectors.keys())
    centroids = []

    for category, tweets in b24_tweets_labeled.items():
        category_tweet_vectors = []
        for t in tweets:
            try:
                category_tweet_vectors.append(list(tweet_vectors[t]))
            except Exception as e:
                pass

        category_centroid = np.array(category_tweet_vectors).mean(axis=0)
        centroids.append(category_centroid)

    # for ctr,pt in enumerate(centroids):
    #     print(categories[ctr])
    #     dist_2 = np.sum((tweet_vectors_values - pt)**2, axis=1)
    #     closest_indices = dist_2.argsort()[:10]
    #     for ci in closest_indices:
    #         print(tweet_vectors_keys[ci])
    #     print('\n')


    # pca = PCA(n_components=2).fit(centroids)
    # pca_2d = pca.transform(centroids)
    # plt.scatter(pca_2d[:, 0], pca_2d[:, 1])

    # for ctr, category in enumerate(categories):
    #     plt.annotate(category, (pca_2d[:, 0][ctr], pca_2d[:, 1][ctr]))

    # plt.show()

    distances = euclidean_distances(centroids)
    print(distances)

    # for category, tweets in b24_tweets_labeled.items():
    #     print(category)
    #     words = []
    #     for t in tweets:
    #         words += clean_tweet(clean_b24_tweet(t, category)).split()
    #     print(Counter(words).most_common(20))


if __name__ == '__main__':
    #build_data()
    #train_w2v()
    cluster_tweets()
    get_accuracy('src/NLP/junk/testing_on_brand24/data/clusters.pkl')

    #visualize_clusters()
    # get_accuracy('src/NLP/junk/testing_on_brand24/data/clusters.pkl')

    # remove_false_football_tweets()

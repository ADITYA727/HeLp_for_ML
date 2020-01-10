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
from gensim.models import KeyedVectors

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')
from src.NLP.preprocessing import clean_tweet, stopwords
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query


def get_data():
    documents = []
    labels = []
    with open('tag_my_news.txt') as f:
        for ctr, line in enumerate(f):
            line_number = ctr + 1
            if line_number % 8 == 2:
                documents.append(line)
            elif line_number % 8 == 7:
                labels.append(line)

    documents_dict = {}
    for d, l in zip(documents, labels):
        l = l.strip('\n')
        d = d.strip('\n')
        if l in documents_dict:
            documents_dict[l].append(d)
        else:
            documents_dict[l] = [d]

    joblib.dump(documents_dict, 'src/NLP/junk/testing_on_brand24/data/tmn_documents_dict.pkl')


def cluster_tweets():
    # word_vectors = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
    # joblib.dump(word_vectors, 'src/NLP/junk/testing_on_brand24/data/google_word_vectors.pkl')

    # word_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/google_word_vectors.pkl')
    documents_dict = joblib.load('src/NLP/junk/testing_on_brand24/data/tmn_documents_dict.pkl')
    documents_list = list(itertools.chain.from_iterable(list(documents_dict.values())))

    # document_vectors = {}
    # for d in documents_list:
    #     document_word_vectors = []
    #     document_words = clean_tweet(d).split()
    #     for word in document_words:
    #         if word in word_vectors:
    #             word_vector = word_vectors[word]
    #             document_word_vectors.append(list(word_vector))

    #     if len(document_word_vectors) > 0:
    #         document_vector = np.array(document_word_vectors).mean(axis=0)
    #         document_vectors[d] = document_vector

    # joblib.dump(document_vectors, 'src/NLP/junk/testing_on_brand24/data/tmn_document_vectors.pkl')

    document_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/tmn_document_vectors.pkl')
    document_vectors_values = list(document_vectors.values())
    n_clusters = 7
    spectral = SpectralClustering(n_clusters=n_clusters)
    spectral.fit(document_vectors_values)
    labels = list(spectral.labels_)

    clusters = {}
    for ctr, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(documents_list[ctr])
        else:
            clusters[label] = [documents_list[ctr]]

    joblib.dump(clusters, 'src/NLP/junk/testing_on_brand24/data/tmn_clusters.pkl')


def get_documents_categories():
    documents_categories = {}
    documents_dict = joblib.load('src/NLP/junk/testing_on_brand24/data/tmn_documents_dict.pkl')
    for category, documents_list in documents_dict.items():
        for d in documents_list:
            documents_categories[d] = category

    return documents_categories


def get_accuracy():
    document_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/tmn_document_vectors.pkl')
    documents_categories = get_documents_categories()
    clusters = joblib.load('src/NLP/junk/testing_on_brand24/data/tmn_clusters.pkl')
    predicted_clusters = {}
    for category in ['sport', 'business', 'entertainment', 'us', 'world', 'health', 'sci_tech']:
        predicted_clusters[category] = []

    ctr = 1
    correct_count = 0
    for label, documents in clusters.items():
        actual_categories = []
        for d in documents:
            actual_category = documents_categories[d]
            actual_categories.append(actual_category)
        print('Cluster ', str(ctr))
        print(Counter(actual_categories))
        accuracy_percent = int((Counter(actual_categories).most_common(1)[0][1]/len(documents)) * 100)
        print('Cluster length: ', len(documents))
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

    overall_accuracy_percent = round((correct_count/len(document_vectors)) * 100, 2)

    print('*'*50 + '\n')
    print('Overall accuracy: {}%'.format(overall_accuracy_percent))


if __name__ == '__main__':
    # get_data()
    cluster_tweets()
    get_accuracy()

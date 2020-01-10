import os
import sys
import random
import numpy as np
import joblib
import itertools
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim.models import Word2Vec
from sklearn.decomposition import TruncatedSVD
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')
from src.NLP.preprocessing import clean_tweet, stopwords

SAMPLE_SIZE = 22000
categories = [
    'Sports_and_Outdoors', 'Electronics', 'Movies_and_TV', 'Clothing_Shoes_and_Jewelry',
    'Home_and_Kitchen', 'Health_and_Personal_Care', 'Toys_and_Games', 'Beauty', 'Apps_for_Android',
    'Office_Products', 'Pet_Supplies', 'Automotive', 'Grocery_and_Gourmet_Food', 'Patio_Lawn_and_Garden',
    'Baby', 'Digital_Music'
]


def get_data():
    reviews_dict = joblib.load('src/NLP/junk/testing_on_snap/data/w2v_outputs/reviews_dict.pkl')
    reviews_lists = list(reviews_dict.values())
    all_reviews = list(itertools.chain.from_iterable(reviews_lists))
    return all_reviews


def get_documents(reviews):
    tagged_documents = []
    for ctr, review in enumerate(reviews):
        tagged_documents.append(TaggedDocument(review, [ctr]))

    return tagged_documents


def train_d2v():
    all_reviews = get_data()
    clean_reviews = [clean_tweet(review, as_string=False) for review in all_reviews]
    documents = get_documents(clean_reviews)
    model = Doc2Vec(documents=documents, dm=1, size=200, window=5, min_count=10)
    review_vectors = {}
    for ctr, r in enumerate(all_reviews):
        review_vectors[r] = model.docvecs[ctr]

    joblib.dump(review_vectors, 'src/NLP/junk/testing_on_snap/data/d2v_outputs/d2v_review_vectors.pkl')


def cluster_reviews():
    all_reviews = get_data()

    review_vectors = joblib.load('src/NLP/junk/testing_on_snap/data/d2v_outputs/d2v_review_vectors.pkl')
    review_vectors_values = list(review_vectors.values())

    n_clusters = 16
    k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    k_means.fit(review_vectors_values)
    labels = list(k_means.labels_)

    clusters = {}
    for ctr, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(all_reviews[ctr])
        else:
            clusters[label] = [all_reviews[ctr]]

    joblib.dump(clusters, 'src/NLP/junk/testing_on_snap/data/d2v_outputs/d2v_clusters.pkl')


def get_reviews_topics():
    reviews_topics = {}
    reviews_dict = joblib.load('src/NLP/junk/testing_on_snap/data/w2v_outputs/reviews_dict.pkl')
    for category, reviews_list in reviews_dict.items():
        for review in reviews_list:
            reviews_topics[review] = category

    return reviews_topics


def get_accuracy():
    reviews_topics = get_reviews_topics()
    clusters = joblib.load('src/NLP/junk/testing_on_snap/data/d2v_outputs/d2v_clusters.pkl')
    predicted_clusters = {}
    for category in categories:
        predicted_clusters[category] = []

    ctr = 1
    correct_count = 0
    for label, reviews in clusters.items():
        actual_categories = []
        for review in reviews:
            actual_category = reviews_topics[review]
            actual_categories.append(actual_category)
        print('Cluster ', str(ctr))
        print(Counter(actual_categories))
        accuracy_percent = int((Counter(actual_categories).most_common(1)[0][1]/len(reviews)) * 100)
        category = Counter(actual_categories).most_common(1)[0][0]
        predicted_clusters[category].append('{}%'.format(accuracy_percent))
        print('\n')
        correct_count += Counter(actual_categories).most_common(1)[0][1]
        ctr += 1

    for category, accuracies in predicted_clusters.items():
        print(category)
        print('Clusters: %s' % len(accuracies))
        if len(accuracies) > 0:
            print('Accuracies: %s' % ', '.join(accuracies))
        print('\n')

    overall_accuracy_percent = (correct_count/341745) * 100
    print('Overall accuracy: {}%'.format(overall_accuracy_percent))


if __name__ == '__main__':
    get_accuracy()

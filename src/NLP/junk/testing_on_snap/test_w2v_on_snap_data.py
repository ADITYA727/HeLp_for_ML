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


def build_data():
    reviews = {}

    for category in categories:
        print(category)
        file_name = 'reviews_%s_5.json' % category
        review_texts = [
            eval(line.rstrip('\n'))['reviewText'] for line in open('src/NLP/junk/testing_on_snap/data/%s' % file_name)
        ]
        sample_size = min(SAMPLE_SIZE, len(review_texts))
        random_sample = [review_texts[i] for i in sorted(random.sample(range(len(review_texts)), sample_size))]
        reviews[category] = random_sample

    joblib.dump(reviews, 'src/NLP/junk/testing_on_snap/data/w2v_outputs/reviews_dict.pkl')


def get_data():
    reviews_dict = joblib.load('src/NLP/junk/testing_on_snap/data/w2v_outputs/reviews_dict.pkl')
    reviews_lists = list(reviews_dict.values())
    all_reviews = list(itertools.chain.from_iterable(reviews_lists))
    return all_reviews


def train_w2v():
    all_reviews = get_data()
    clean_reviews = [clean_tweet(review, as_string=False) for review in all_reviews]
    model = Word2Vec(sentences=clean_reviews, sg=1, size=200, window=5, min_count=10)
    word_vectors = {}
    for word in model.wv.vocab:
        word_vectors[word] = model[word]

    joblib.dump(word_vectors, 'src/NLP/junk/testing_on_snap/data/w2v_outputs/w2v_word_vectors_only_nouns.pkl')

    return model


def cluster_reviews():
    word_vectors = joblib.load('src/NLP/junk/testing_on_snap/data/w2v_outputs/w2v_word_vectors_only_nouns.pkl')

    all_reviews = get_data()

    review_vectors = {}
    for review in all_reviews:
        review_word_vectors = []
        review_words = clean_tweet(review).split()
        for word in review_words:
            if word in word_vectors:
                word_vector = word_vectors[word]
                review_word_vectors.append(list(word_vector))

        if len(review_word_vectors) > 0:
            review_vector = np.array(review_word_vectors).mean(axis=0)
            review_vectors[review] = review_vector

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

    joblib.dump(clusters, 'src/NLP/junk/testing_on_snap/data/w2v_outputs/w2v_clusters_only_nouns.pkl')


def get_reviews_topics():
    reviews_topics = {}
    reviews_dict = joblib.load('src/NLP/junk/testing_on_snap/data/w2v_outputs/reviews_dict.pkl')
    for category, reviews_list in reviews_dict.items():
        for review in reviews_list:
            reviews_topics[review] = category

    return reviews_topics


def get_accuracy():
    reviews_topics = get_reviews_topics()
    clusters = joblib.load('src/NLP/junk/testing_on_snap/data/w2v_outputs/w2v_clusters_only_nouns.pkl')
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

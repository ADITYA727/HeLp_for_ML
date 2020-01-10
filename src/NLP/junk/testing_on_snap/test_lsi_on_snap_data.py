import os
import sys
import random
import numpy as np
import joblib
import itertools
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')
from src.NLP.preprocessing import clean_tweet, stopwords
from src.NLP.junk.lsi_on_tweets import silhouette_samples_memory_saving

SAMPLE_SIZE = 14000
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
            eval(line.rstrip('\n'))['reviewText'] for line in open('src/NLP/junk/test_lsi/data/%s' % file_name)
        ]
        sample_size = min(SAMPLE_SIZE, len(review_texts))
        random_sample = [review_texts[i] for i in sorted(random.sample(range(len(review_texts)), sample_size))]
        reviews[category] = random_sample

    joblib.dump(reviews, 'src/NLP/junk/test_lsi/data/reviews_dict.pkl')


def get_data():
    reviews_dict = joblib.load('src/NLP/junk/test_lsi/data/reviews_dict.pkl')
    reviews_lists = list(reviews_dict.values())
    all_reviews = list(itertools.chain.from_iterable(reviews_lists))
    return all_reviews


def cluster_reviews():
    reviews = get_data()

    vectorizer = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords, max_df=0.02, preprocessor=clean_tweet)
    vector_matrix = vectorizer.fit_transform(reviews)

    lsa = TruncatedSVD(n_components=200, algorithm='arpack')
    vector_lsa = lsa.fit_transform(vector_matrix)

    n_clusters = 16
    k_means = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100)
    k_means.fit(vector_lsa)

    # label = k_means.labels_
    # sil_coeff = np.mean(silhouette_samples_memory_saving(vector_lsa, label, metric='euclidean'))
    # print(sil_coeff)

    weights = np.dot(k_means.cluster_centers_, lsa.components_)
    features = vectorizer.get_feature_names()
    weights = np.abs(weights)

    for i in range(k_means.n_clusters):
        top = np.argsort(weights[i])[-20:]
        print([features[j] for j in top])


def get_accuracy_preprocessing():
    reviews_dict = joblib.load('src/NLP/junk/test_lsi/data/reviews_dict.pkl')
    topic_words_count = {}
    for topic, reviews in reviews_dict.items():
        words = clean_tweet(' '.join(reviews)).split()
        topic_words_count[topic] = dict(Counter(words))

    joblib.dump(topic_words_count, 'src/NLP/junk/test_lsi/data/topic_words_count.pkl')


def get_topic_of_word(topics):
    topic_words_count = joblib.load('src/NLP/junk/test_lsi/data/topic_words_count.pkl')
    word_topic = {}
    word_topics = {}

    words = list(itertools.chain.from_iterable(topics))
    for word in words:
        for topic, words_count in topic_words_count.items():
            if word in word_topics:
                word_topics[word].append((topic, words_count.get(word, 0)))
            else:
                word_topics[word] = [(topic, words_count.get(word, 0))]

    for word, topics_count in word_topics.items():
        topics_count.sort(key=lambda x: x[1], reverse=True)
        top_topic = topics_count[0][0]
        word_topic[word] = top_topic

    return word_topic


def get_accuracy():
    clusters = {}
    for category in categories:
        clusters[category] = []

    topics = [
        ['silky', 'rinse', 'suave', 'oil', 'curly', 'conditioners', 'results', 'oily', 'wash', 'feeling', 'shampoos', 'shiny', 'shower', 'dandruff', 'smells', 'leaves', 'scent', 'scalp', 'conditioner', 'shampoo'],
        ['kershaw', 'sharpening', 'opening', 'lock', 'tool', 'sharpen', 'razor', 'clip', 'edc', 'carry', 'grip', 'cutting', 'steel', 'pocket', 'edge', 'sheath', 'knives', 'sharp', 'blade', 'knife'],
        ['items', 'lots', 'pleased', 'christmas', 'feet', 'tight', 'likes', 'pair', 'picture', 'toys', 'batteries', 'glad', 'shoes', 'husband', 'pack', 'tape', 'durable', 'wash', 'gift', 'oil'],
        ['feeding', 'metal', 'hang', 'red', 'perky', 'nectar', 'feed', 'pet', 'seeds', 'glass', 'squirrel', 'hummingbirds', 'hummingbird', 'fill', 'squirrels', 'seed', 'feeders', 'bird', 'birds', 'feeder'],
        ['setup', 'laser', 'network', 'scan', 'fax', 'software', 'scanner', 'photos', 'photo', 'prints', 'wireless', 'cartridge', 'printers', 'canon', 'epson', 'cartridges', 'printing', 'print', 'ink', 'printer'],
        ['carseat', 'safety', 'safe', 'tray', 'toilet', 'potty', 'strap', 'base', 'rear', 'child', 'booster', 'facing', 'sit', 'britax', 'infant', 'straps', 'seats', 'chair', 'stroller', 'seat'],
        ['ads', 'shows', 'level', 'please', 'android', 'boring', 'device', 'puzzles', 'screen', 'challenging', 'tablet', 'levels', 'graphics', 'fire', 'downloaded', 'phone', 'download', 'apps', 'kindle', 'app'],
        ['page', 'tabs', 'sheet', 'durable', 'spine', 'inch', 'dividers', 'covers', 'duty', 'notebook', 'sheets', 'school', 'papers', 'pages', 'pocket', 'ring', 'pockets', 'binders', 'rings', 'binder'],
        ['coins', 'enjoyed', 'puzzles', 'card', 'level', 'puzzle', 'cards', 'objects', 'board', 'learning', 'challenge', 'object', 'kindle', 'app', 'hidden', 'word', 'graphics', 'challenging', 'played', 'games'],
        ['fans', 'title', 'collection', 'disc', 'guitar', 'sounds', 'record', 'heard', 'hits', 'voice', 'classic', 'pop', 'listen', 'lyrics', 'band', 'albums', 'rock', 'tracks', 'amp', 'quot'],
        ['dark', 'french', 'smooth', 'blend', 'tastes', 'coffees', 'bold', 'brew', 'flavored', 'filter', 'bitter', 'morning', 'pot', 'keurig', 'roast', 'drink', 'maker', 'cups', 'cup', 'coffee'],
        ['printed', 'shipping', 'inkjet', 'post', 'file', 'templates', 'printing', 'folders', 'word', 'template', 'adhesive', 'laser', 'address', 'sheet', 'peel', 'printer', 'print', 'avery', 'label', 'labels'],
        ['blush', 'comb', 'apply', 'bottles', 'wheels', 'cleaner', 'wheel', 'tooth', 'heads', 'makeup', 'brushing', 'powder', 'grill', 'foundation', 'toothbrush', 'cleaning', 'teeth', 'bristles', 'brushes', 'brush'],
        ['stores', 'pleased', 'customer', 'glad', 'convenient', 'gift', 'reading', 'delivery', 'mom', 'please', 'seller', 'arrived', 'app', 'summer', 'looked', 'complaints', 'ordering', 'shipping', 'service', 'thanks'],
        ['teas', 'chicken', 'ingredients', 'bed', 'cup', 'vet', 'ball', 'bags', 'pet', 'green', 'drink', 'toys', 'treat', 'eat', 'treats', 'litter', 'tea', 'cats', 'dogs', 'cat'],
        ['reading', 'levels', 'plays', 'device', 'addicting', 'pit', 'facebook', 'deleted', 'computer', 'download', 'phone', 'played', 'apps', 'games', 'graphics', 'downloaded', 'screen', 'app', 'fire', 'kindle'],
    ]

    correct_count = 0
    word_topic = get_topic_of_word(topics)
    for topic in topics:
        labels = []
        for word in topic:
            topic_label = word_topic[word]
            labels.append(topic_label)

        category = Counter(labels).most_common(1)[0][0]
        correct_count += Counter(labels).most_common(1)[0][1]
        accuracy_percent = int((Counter(labels).most_common(1)[0][1]/20) * 100)
        clusters[category].append('{}%'.format(accuracy_percent))

    for category, accuracies in clusters.items():
        print(category)
        print('Clusters: %s' % len(accuracies))
        if len(accuracies) > 0:
            print('Accuracies: %s' % ', '.join(accuracies))
        print('\n')

    overall_accuracy_percent = (correct_count/(len(clusters) * 20)) * 100
    print('Overall accuracy: {}%'.format(overall_accuracy_percent))


if __name__ == '__main__':
    get_accuracy()

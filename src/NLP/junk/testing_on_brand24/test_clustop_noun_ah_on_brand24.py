import os
import sys
import joblib
import re
import itertools
import numpy as np
import networkx as nx
import community
from collections import Counter
from nltk import pos_tag
from nltk.tokenize import word_tokenize

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')

from src.NLP.preprocessing import clean_tweet, stopwords, links, twitter_pic
from src.NLP.junk.testing_on_brand24.test_w2v_on_brand24 import get_b24_tweets, categories


def cluster_tweets_based_on_noun():
    tweets = get_b24_tweets()
    nouns = []
    tweets_nouns = []
    hashtags = []
    tweets_hashtags = []
    tweets_reduced_dict = {}
    tweets_aggregated = []

    for idx, tweet in enumerate(tweets):
        # pyquery cleaning
        corrections = [
            ('http:// ', 'http://'),
            ('https:// ', 'https://'),
            ('http://www. ', 'http://www.'),
            ('https://www. ', 'https://www.'),
            ('pic.twitter.com', 'https://pic.twitter.com'),
            ('# ', '#')
        ]
        for correction in corrections:
            tweet = tweet.replace(correction[0], correction[1])

        tweet = links.sub('', tweet)
        tweet = twitter_pic.sub('', tweet)

        tweet_hashtags = re.findall(r'#(\w+)', tweet)
        hashtags += tweet_hashtags
        if len(tweet_hashtags) > 0:
            l = list(set(map(str.lower, tweet_hashtags)))
            tweets_hashtags.append(l)
            key = '||'.join(l)
            if key in tweets_reduced_dict:
                tweets_reduced_dict[key].append(idx)
            else:
                tweets_reduced_dict[key] = [idx]

    for k,v in tweets_reduced_dict.items():
        tweets_aggregated.append(' '.join([tweets[x] for x in v]))


    for tweet in tweets_aggregated:
        # pyquery cleaning
        corrections = [
            ('http:// ', 'http://'),
            ('https:// ', 'https://'),
            ('http://www. ', 'http://www.'),
            ('https://www. ', 'https://www.'),
            ('pic.twitter.com', 'https://pic.twitter.com'),
            ('# ', '#')
        ]
        for correction in corrections:
            tweet = tweet.replace(correction[0], correction[1])

        tweet = links.sub('', tweet)
        tweet = twitter_pic.sub('', tweet)

        tweet = ' '.join([word[0] for word in pos_tag(word_tokenize(tweet)) if word[1].startswith('NN')])
        tweet_nouns = tweet.split()
        nouns += tweet_nouns
        if len(tweet_nouns) > 0:
            tweets_nouns.append(list(set(map(str.lower, tweet_nouns))))

    nouns = list(set(map(str.lower, nouns)))
    joblib.dump(nouns, 'src/NLP/junk/testing_on_brand24/data/clustop_nouns.pkl')
    # joblib.dump(tweets_nouns, 'src/NLP/junk/testing_on_brand24/data/clustop_tweets_nouns.pkl')

    # tweets_nouns = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_tweets_nouns.pkl')
    # nouns = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_nouns.pkl')

    nouns_dict = {}
    for ctr, h in enumerate(nouns):
        nouns_dict[h] = ctr
    nouns_count = len(nouns)

    co_occurence_matrix = np.zeros((nouns_count, nouns_count))

    for elem in tweets_nouns:
        for combination in itertools.combinations(elem, 2):
            h1 = combination[0]
            h2 = combination[1]
            position1 = nouns_dict[h1]
            position2 = nouns_dict[h2]
            co_occurence_matrix[position1, position2] += 1
            co_occurence_matrix[position2, position1] += 1

    G = nx.from_numpy_matrix(co_occurence_matrix)
    labels = community.best_partition(G)
    joblib.dump(labels, 'src/NLP/junk/testing_on_brand24/data/clustop_labels.pkl')


def get_communities():
    communities = {}
    nouns = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_nouns.pkl')
    labels = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_labels.pkl')

    for noun_index, label in labels.items():
        noun = nouns[noun_index]
        if label in communities:
            communities[label].append(noun)
        else:
            communities[label] = [noun]

    joblib.dump(communities, 'src/NLP/junk/testing_on_brand24/data/clustop_communities.pkl')

    # communities_len = {}
    # for label, nouns in communities.items():
    #     communities_len[label] = len(nouns)

    # print(len(communities_len))
    # ctr = 1
    # for key in sorted(communities_len, key=communities_len.get, reverse=True)[:50]:
    #     print('Community ' + str(ctr))
    #     print(communities[key][:150])
    #     print(len(communities[key]))
    #     print('\n')
    #     ctr += 1


def get_accuracy_preprocessing():
    b24_tweets_labeled = joblib.load('src/NLP/junk/testing_on_brand24/data/b24_tweets_labeled.pkl')
    topic_words_count = {}
    for topic, tweets in b24_tweets_labeled.items():
        words = clean_tweet(' '.join(tweets)).split()
        topic_words_count[topic] = dict(Counter(words))

    joblib.dump(topic_words_count, 'src/NLP/junk/testing_on_brand24/data/clustop_topic_words_count.pkl')


def get_nouns_categories(clusters):
    topic_words_count = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_topic_words_count.pkl')
    word_topic = {}
    word_topics = {}

    words = list(itertools.chain.from_iterable(list(clusters.values())))
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
    clusters = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_communities.pkl')
    nouns_categories = get_nouns_categories(clusters)
    predicted_clusters = {}
    for category in categories:
        predicted_clusters[category] = []

    ctr = 1
    correct_count = 0
    for label, nouns in clusters.items():
        actual_categories = []
        for h in nouns:
            actual_category = nouns_categories[h]
            actual_categories.append(actual_category)
        print('Cluster ', str(ctr))
        print(Counter(actual_categories))
        accuracy_percent = int((Counter(actual_categories).most_common(1)[0][1]/len(nouns)) * 100)
        print('Cluster length: ', len(nouns))
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

    total_nouns = list(itertools.chain.from_iterable(list(clusters.values())))
    overall_accuracy_percent = round((correct_count/len(total_nouns)) * 100, 2)

    print('*'*50 + '\n')
    print('Overall accuracy: {}%'.format(overall_accuracy_percent))


if __name__ == '__main__':
    cluster_tweets_based_on_noun()
    get_communities()
    get_accuracy_preprocessing()
    get_accuracy()

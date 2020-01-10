import os
import sys
import joblib
import re
import itertools
import numpy as np
import networkx as nx
import community
from collections import Counter

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')

from src.NLP.preprocessing import clean_tweet, stopwords, links, twitter_pic
from src.NLP.junk.testing_on_brand24.test_w2v_on_brand24 import get_b24_tweets, categories


def cluster_tweets_based_on_hashtag():
    tweets = get_b24_tweets()
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

    hashtags = []
    tweets_hashtags = []

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

        tweet_hashtags = re.findall(r'#(\w+)', tweet)
        hashtags += tweet_hashtags
        if len(tweet_hashtags) > 0:
            tweets_hashtags.append(list(set(map(str.lower, tweet_hashtags))))

    hashtags = list(set(map(str.lower, hashtags)))
    joblib.dump(hashtags, 'src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_hashtags.pkl')
    # joblib.dump(tweets_hashtags, 'src/NLP/junk/testing_on_brand24/data/clustop_tweets_hashtags.pkl')

    # tweets_hashtags = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_tweets_hashtags.pkl')
    # hashtags = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_hashtags.pkl')

    hashtags_dict = {}
    for ctr, h in enumerate(hashtags):
        hashtags_dict[h] = ctr
    hashtags_count = len(hashtags)

    co_occurence_matrix = np.zeros((hashtags_count, hashtags_count))

    for elem in tweets_hashtags:
        for combination in itertools.combinations(elem, 2):
            h1 = combination[0]
            h2 = combination[1]
            position1 = hashtags_dict[h1]
            position2 = hashtags_dict[h2]
            co_occurence_matrix[position1, position2] += 1
            co_occurence_matrix[position2, position1] += 1

    G = nx.from_numpy_matrix(co_occurence_matrix)
    labels = community.best_partition(G)
    joblib.dump(labels, 'src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_labels.pkl')


def get_communities():
    communities = {}
    hashtags = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_hashtags.pkl')
    labels = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_labels.pkl')

    for hashtag_index, label in labels.items():
        hashtag = hashtags[hashtag_index]
        if label in communities:
            communities[label].append(hashtag)
        else:
            communities[label] = [hashtag]

    joblib.dump(communities, 'src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_communities.pkl')

    # communities_len = {}
    # for label, hashtags in communities.items():
    #     communities_len[label] = len(hashtags)

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

    joblib.dump(topic_words_count, 'src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_topic_words_count.pkl')


def get_hashtags_categories(clusters):
    topic_words_count = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_topic_words_count.pkl')
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
    clusters = joblib.load('src/NLP/junk/testing_on_brand24/data/clustop_hash_ah_communities.pkl')
    hashtags_categories = get_hashtags_categories(clusters)
    predicted_clusters = {}
    for category in categories:
        predicted_clusters[category] = []

    ctr = 1
    correct_count = 0
    for label, hashtags in clusters.items():
        actual_categories = []
        for h in hashtags:
            actual_category = hashtags_categories[h]
            actual_categories.append(actual_category)
        print('Cluster ', str(ctr))
        print(Counter(actual_categories))
        accuracy_percent = int((Counter(actual_categories).most_common(1)[0][1]/len(hashtags)) * 100)
        print('Cluster length: ', len(hashtags))
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

    total_hashtags = list(itertools.chain.from_iterable(list(clusters.values())))
    overall_accuracy_percent = round((correct_count/len(total_hashtags)) * 100, 2)

    print('*'*50 + '\n')
    print('Overall accuracy: {}%'.format(overall_accuracy_percent))


if __name__ == '__main__':
    cluster_tweets_based_on_hashtag()
    get_communities()
    get_accuracy_preprocessing()
    get_accuracy()

import os
import sys
import joblib
import numpy as np
from collections import OrderedDict
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import get_data
from src.NLP.preprocessing import clean_tweet, stopwords


def get_topics_of_users():
    user_tweets, users_retweets_count, all_retweet_count = get_data(offset=1200, length=1)
    tf_idf_vectorizer = joblib.load('src/NLP/junk/lsi_output_vectorizer.pkl')
    topic_matrix = joblib.load('src/NLP/junk/lsi_output_weights.pkl')
    topic_matrix_csr = sparse.csr_matrix(topic_matrix)
    feature_names = tf_idf_vectorizer.get_feature_names()

    topics = {
        0: 'Politics 1',
        1: 'Politics 2',
        2: 'Politics(UP)',
        3: 'Independence',
        4: 'Tech Quiz',
        5: 'Woman empowerment',
        6: 'Hindi/Non-English 1',
        7: 'Photography 1',
        8: 'Plastic',
        9: 'Children',
        10: 'ISL 1',
        11: 'Wishes/Appreciation',
        12: 'Industry',
        13: 'Social Campaign',
        14: 'Valentines Day',
        15: 'Follow 1',
        16: 'Hindi/Non-English 2',
        17: 'Bollywood',
        18: 'Hate/Love feelings',
        19: 'Politics 3',
        20: 'New year',
        21: 'Follow 2',
        22: 'Special Wishes',
        23: 'Photography 2',
        24: 'Daily wishes',
        25: 'Cancer',
        26: 'ISL 2',
        27: 'Songs',
        28: 'Hindi words in english font',
        29: 'Hindi/Non-English 3'
    }

    for user_handle, tweet_text in user_tweets.items():
        print(user_handle)
        print('https://twitter.com/%s' % user_handle[1:])
        count_vectorizer = CountVectorizer(
            strip_accents='ascii', stop_words=stopwords, preprocessor=clean_tweet, binary=False,
            vocabulary=feature_names
        )
        count_vectorizer_matrix = count_vectorizer.fit_transform([tweet_text])
        count_vectorizer_idf_matrix = sparse.csr_matrix(
            np.multiply(count_vectorizer_matrix.toarray(), tf_idf_vectorizer.idf_)
        )
        topic_weights = np.dot(count_vectorizer_idf_matrix, topic_matrix_csr.T).toarray()[0]
        topic_weights_dict = {}
        for ctr, topic_weight in enumerate(topic_weights):
            topic_weights_dict[topics[ctr]] = topic_weight

        topic_weights_dict = OrderedDict(sorted(topic_weights_dict.items(), key=lambda x: x[1], reverse=True))
        topic_weights_sum = sum(topic_weights_dict.values())

        print('Topics:\n')
        for topic, weight in topic_weights_dict.items():
            print('{}: {}({} %)'.format(topic, round(weight, 4), round(((weight/topic_weights_sum)*100), 2)))


if __name__ == '__main__':
    get_topics_of_users()

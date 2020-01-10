# Information
# Retrieval
# Florida Atlantic University, Fall 2017
# Justin Johnson jjohn273

import os
import sys
import operator
from sklearn.decomposition import TruncatedSVD
from sklearn import pipeline
from sklearn.preprocessing import Normalizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import joblib
import gensim
from gensim import corpora
import numpy as np
import re
from nltk.data import path
from pprint import pprint

path.append("/home/analytics/data_partition/nltk_data")
from nltk.corpus import stopwords

stops = set(stopwords.words('english'))
import warnings

warnings.filterwarnings('ignore')

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.mysql_utils import MySqlUtils
from src.NLP.preprocessing import clean_tweet

Lda = gensim.models.ldamodel.LdaModel

threshold = 0.95


def double_quote(word):
    # return f'"{word}"' # python 3.6 onwards
    return '"{}"'.format(word)


def get_nth_key(dictionary, n=0):
    if n < 0:
        n += len(dictionary)
    for i, key in enumerate(dictionary.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")


# run python src/scraping/state_and_cities.py
cities_list = joblib.load(home + '/../../data/cities.txt')
states_list = joblib.load(home + '/../../data/states.txt')

cities_query = ' '.join([double_quote(city.lower()) for city in cities_list])
states_query = ' '.join([double_quote(state.lower()) for state in states_list])
combined_query = double_quote('india') + ' ' + cities_query + ' ' + states_query
cleaned_query = ' '.join([data for data in combined_query.split('(')])
final_query = cleaned_query.replace(')', '')

user_query = """SELECT queue.user_handle FROM
                  queue JOIN user
                  ON queue.user_handle = user.user_handle
                  WHERE
                  queue.tweet_status=1 AND user.lang='en' AND
                  user.total_tweet_count > 25 AND queue.query_id=1 AND
                      MATCH (user.location, user.time_zone, user.description) AGAINST ('{}' IN BOOLEAN MODE);""".format(final_query)

#print(user_query)



def vectorize_w2v(doc):
    """Identify the vector values for each word in the given document"""
    word_vecs = []
    for word in doc:
        try:
            vec = w2v_model[word]
            word_vecs.append(vec)
        except KeyError:
            # Ignore, if the word doesn't exist in the vocabulary
            pass
    vector = np.mean(word_vecs, axis=0)
    if not (vector.shape):
        vector = np.zeros((1, 300))
    return vector


def get_data(length=500000, offset=0):
    """build corpus: list of tweets from twitter account


    :param length: To avoid memory explosion
    :return:
    """
    sql = MySqlUtils()
    users = sql.get_data(user_query)
    users_list = [user['user_handle'] for user in users[offset:(offset + length)]]
    print('Query count {}'.format(len(users)))
    query = 'SELECT text, user_handle, retweets, retweets_permalink FROM tweet where user_handle IN (' + ','.join(
        ("'{}'".format(user) for user in users_list)) + ')'

    tweets = sql.get_data(query)
    corpus = dict()
    users_retweets_count = dict()
    print("Tweets", len(tweets))
    retweets = []
    user_handle = ''
    all_retweet_count = []

    for tweet in tweets:
        if tweet['user_handle'] not in corpus:
            if user_handle:
                users_retweets_count[user_handle] = np.sum(retweets)
                all_retweet_count.extend(retweets)
            retweets = []
            user_handle = tweet['user_handle']
            corpus[tweet['user_handle']] = tweet['text']
            if tweet['retweets_permalink']:
                retweets.append(0)
            else:
                retweets.append(tweet['retweets'])
        else:
            corpus[tweet['user_handle']] = corpus[tweet['user_handle']] + '. ' + tweet['text']
            if tweet['retweets_permalink']:
                retweets.append(0)
            else:
                retweets.append(tweet['retweets'])
    # for last user_handle
    all_retweet_count.extend(retweets)
    users_retweets_count[user_handle] = np.sum(retweets)
    for user_handle, text in corpus.items():
        # TODO: Too Slow. Speed this up
        tokens = clean_tweet(text, stem=False, lemmatize=False, as_string=False)

        corpus[user_handle] = ' '.join(tokens, )
    return corpus, users_retweets_count, np.sum(all_retweet_count)


def get_user_descriptions(length=500000):
    """build corpus: list of tweets from twitter account


    :param length: To avoid memory explosion
    :return:
    """
    sql = MySqlUtils()
    users = sql.get_data(user_query)
    users_list = [user['user_handle'] for user in users[:length]]
    print('Query count {}'.format(len(users)))
    query = 'SELECT description, user_handle FROM user where user_handle IN (' + ','.join(
        ("'{}'".format(user) for user in users_list)) + ')'

    descriptions = sql.get_data(query)
    corpus = dict()
    print("Descriptions", len(descriptions))

    for row in descriptions:
        text = row['description']
        user_handle = row['user_handle']
        if len(text) > 0:
            tokens = clean_tweet(text, stem=False, lemmatize=False, as_string=False)
            corpus[user_handle] = ' '.join(tokens)
    return corpus


def vectorize_corpus(corpus, lsa=0):
    """
    :param corpus:
    :param lsa:
    :return:
    """
    # Using sklearn's tfidfvectorizer to construct tfidf matrix
    vectorizer = TfidfVectorizer()
    vector_matrix = vectorizer.fit_transform(corpus.values())
    # applied lsa and svd
    if lsa:
        svd = TruncatedSVD(lsa)
        lsa = pipeline.make_pipeline(svd, Normalizer(copy=False))
        vector_matrix = lsa.fit_transform(vector_matrix)
    return vector_matrix


def get_clusters(matrix, corpus):
    """Using sklearn's cosine_similarty to calculate cosine similarity between all documents


    :param matrix:
    :param corpus:
    :return:
    """
    cos_sim_matrix = cosine_similarity(matrix)
    # Using sklearn's cosine_similarty to calculate cosine similarity between all documents
    print("Matrix Mean: {}".format(cos_sim_matrix.mean()))
    mat = np.where(cos_sim_matrix > threshold, 1, 0)
    # Get clusters using networkx
    network = nx.from_numpy_matrix(mat)
    clusters = list(nx.connected_components(network))
    # clusters contains indexes of users in corpus dictionary.
    users_cluster = []
    for cluster in clusters:
        if len(cluster) > 1:
            users = []
            for item in cluster:
                users.append(get_nth_key(corpus, item))
                print(get_nth_key(corpus, item))
            print('\n')
            users_cluster.append(users)
    return users_cluster


def vectorize_corpus_w2v(corpus):
    """Calculates & returns similarity scores between given documents"""
    corpus_mat = None
    for doc in list(corpus.values()):
        if corpus_mat is None:
            corpus_mat = vectorize_w2v(doc)
        else:
            corpus_mat = np.row_stack((corpus_mat, vectorize_w2v(doc)))
    return corpus_mat


def get_users_score(users_retweets_count, all_retweet_count):
    sql = MySqlUtils()
    users_details = dict()
    fol_count = 0
    lik_count = 0
    ver_count = 0
    for user_handle, count in users_retweets_count.items():
        query = "SELECT followers_count, likes_count, verified from user WHERE user_handle='{}'".format(user_handle)
        details = sql.get_data(query)
        users_details[user_handle] = [details[0]['followers_count'], details[0]['likes_count'], details[0]['verified'],
                                      count]
        fol_count = fol_count + details[0]['followers_count']
        lik_count = lik_count + details[0]['likes_count']
        ver_count = ver_count + details[0]['verified']

    fol_mean = fol_count / len(users_details)
    lik_mean = lik_count / len(users_details)
    ver_mean = ver_count / len(users_details)
    users_score = {}
    for user_handle in users_details:
        users_score[user_handle] = users_details[user_handle][0] / fol_mean + users_details[user_handle][1] / lik_mean + \
                                   users_details[user_handle][2] / ver_mean + users_details[user_handle][
                                       3] / all_retweet_count

    return users_score


def get_top_followers():
    sql = MySqlUtils()
    users_score = joblib.load('time_22_4_2018_users_score.pkl')
    sorted_scores = sorted(users_score.items(), reverse=True, key=operator.itemgetter(1))[:100]
    results = []
    for item in sorted_scores:
        query = """SELECT * from user where user_handle='%s'""" % (item[0])
        result = sql.get_data(query)
        result = result[0]
        result['score'] = item[1]
        results.append(result)
        # pprint(result)
        # print('\n')

    joblib.dump(results, 'time_22_4_2018_results.pkl')

if __name__ == "__main__":
    get_top_followers()

    # user_tweets, users_retweets_count, all_retweet_count = get_data(length=50000)
    # joblib.dump(user_tweets, 'time_22_4_2018_user_tweets.pkl')
    # joblib.dump(users_retweets_count, 'time_22_4_2018_users_retweets_count.pkl')
    # joblib.dump(all_retweet_count, 'time_22_4_2018_all_retweet_count.pkl')

    # users_score = get_users_score(users_retweets_count, all_retweet_count)
    # joblib.dump(users_score, 'time_22_4_2018_users_score.pkl')

    # user_tweets = get_user_descriptions(length=50000)

    # model_path = 'lib/GoogleNews-vectors-negative300-slim.bin'
    # model_path='data/GoogleNews-vectors-negative300.bin'
    # w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=True)
    # model_path = "data/crawl-300d-2M.vec"
    # w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=False)

    # corpus_matrix = vectorize_corpus(user_tweets, lsa=0)
    # # corpus_matrix = vectorize_corpus_w2v(user_tweets)
    # users_cluster = get_clusters(corpus_matrix, user_tweets)
    # data = []
    # for users in users_cluster:
    #     sort_users = dict()
    #     for user_handle in users:
    #         sort_users[user_handle] = users_score[user_handle]

    #     text_list = [user_tweets[user_handle] for user_handle in users]
    #     doc_clean = [text.split() for text in text_list]
    #     dictionary = corpora.Dictionary(doc_clean)
    #     doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

    #     ldamodel = Lda(doc_term_matrix, num_topics=10, id2word=dictionary, passes=20)

    #     # print(ldamodel.print_topics(num_topics=10, num_words=4))opic
    #     # print(ldamodel.print_topics(num_topics=10, num_words=4)[1])
    #     extract_topic = []
    #     for lda_topic in ldamodel.print_topics(num_topics=10, num_words=6):
    #         extract_topic.extend(re.findall(r'\"(.+?)\"', lda_topic[1]))
    #     extract_topic = list(set(extract_topic))
    #     print(sort_users)

    #     topic_cluster2 = {'user_handles': sorted(sort_users.items(), key=lambda x: x[1], reverse=True),
    #                       'topic': extract_topic}
    #     data.append(topic_cluster2)

    # for text in data:
    #     print("User_handles : ", text['user_handles'])
    #     print("Topic        : ", text['topic'])

    # print("Total Number of profiles selected for clustering {}".format(len(user_tweets)))

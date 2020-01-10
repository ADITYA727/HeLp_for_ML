import os
import sys
import gensim
from gensim import corpora

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.mysql_utils import MySqlUtils
from src.NLP.similarity import user_query
from src.NLP.preprocessing import clean_tweet

Lda = gensim.models.ldamodel.LdaModel


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


def run_lda_on_all_tweets():
    tweets = get_data(length=1500)
    doc_clean = [clean_tweet(tweet['text'], stem=False, lemmatize=False, as_string=False) for tweet in tweets]
    dictionary = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

    ldamodel = Lda(doc_term_matrix, num_topics=15, id2word=dictionary, passes=50)
    topics = ldamodel.print_topics(num_topics=15, num_words=20)

    print(topics)
    for topic in topics:
        print(topic)
        print('*'*80)


if __name__ == '__main__':
    run_lda_on_all_tweets()

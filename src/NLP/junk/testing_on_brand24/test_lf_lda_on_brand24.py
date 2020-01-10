import os
import sys
import gensim
import joblib
import numpy as np
from gensim import corpora

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')

from src.NLP.preprocessing import clean_tweet
from src.NLP.junk.testing_on_brand24.test_w2v_on_brand24 import build_data, get_b24_tweets, get_accuracy

Lda = gensim.models.ldamodel.LdaModel


def run_lda():
    tweets = get_b24_tweets()
    doc_clean = [clean_tweet(tweet, as_string=False) for tweet in tweets]
    dictionary = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

    ldamodel = Lda(doc_term_matrix, num_topics=10, id2word=dictionary, passes=10)
    joblib.dump(ldamodel, '/Users/shashankwadhwa/Desktop/Work/stealth/analytics/src/NLP/junk/testing_on_brand24/data/ldamodel.pkl')
    topics = ldamodel.print_topics(num_topics=10, num_words=20)

    for topic in topics:
        print(topic)
        print('*'*80)


def run_lf_lda():
    base_lda_model = joblib.load('/Users/shashankwadhwa/Desktop/Work/stealth/analytics/src/NLP/junk/testing_on_brand24/data/ldamodel.pkl')
    eta = base_lda_model.get_topics()
    eta_exp = np.exp(eta)
    eta_softmax = eta_exp/eta_exp.sum(axis=1)[:, None]

    tweets = get_b24_tweets()
    doc_clean = [clean_tweet(tweet, as_string=False) for tweet in tweets]
    dictionary = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

    ldamodel = Lda(doc_term_matrix, num_topics=10, id2word=dictionary, passes=10, eta=eta_softmax)
    joblib.dump(ldamodel, '/Users/shashankwadhwa/Desktop/Work/stealth/analytics/src/NLP/junk/testing_on_brand24/data/lf_ldamodel.pkl')
    topics = ldamodel.print_topics(num_topics=10, num_words=20)

    for topic in topics:
        print(topic)
        print('*'*80)


def cluster_tweets():
    model = joblib.load('/Users/shashankwadhwa/Desktop/Work/stealth/analytics/src/NLP/junk/testing_on_brand24/data/lf_ldamodel.pkl')
    tweets = get_b24_tweets()
    doc_clean = [clean_tweet(tweet, as_string=False) for tweet in tweets]
    dictionary = corpora.Dictionary(doc_clean)
    clusters = {}
    for ctr, d in enumerate(doc_clean):
        bow = dictionary.doc2bow(d)
        topics = model.get_document_topics(bow)
        sorted_topics = sorted(topics, key=lambda x: x[1], reverse=True)
        label = sorted_topics[0][0]
        if label in clusters:
            clusters[label].append(tweets[ctr])
        else:
            clusters[label] = [tweets[ctr]]

    joblib.dump(clusters, '/Users/shashankwadhwa/Desktop/Work/stealth/analytics/src/NLP/junk/testing_on_brand24/data/lf_lda_clusters.pkl')


if __name__ == '__main__':
    #build_data()
    #run_lda()
    #run_lf_lda()
    #cluster_tweets()
    get_accuracy('/Users/shashankwadhwa/Desktop/Work/stealth/analytics/src/NLP/junk/testing_on_brand24/data/lf_lda_clusters.pkl')

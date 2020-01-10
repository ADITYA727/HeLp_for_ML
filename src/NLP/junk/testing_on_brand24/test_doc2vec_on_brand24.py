import os
import sys
import gensim
import joblib
from gensim import corpora

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../../')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from src.NLP.preprocessing import clean_tweet, stopwords
from src.NLP.junk.testing_on_brand24.test_w2v_on_brand24 import get_b24_tweets, get_accuracy, get_db_tweets


def get_documents(tweets):
    tagged_documents = []
    for ctr, tweet in enumerate(tweets):
        tagged_documents.append(TaggedDocument(tweet, [ctr]))

    return tagged_documents


def run_d2v():
    b24_all_tweets = get_b24_tweets()
    db_tweets = [t['text'] for t in get_db_tweets(length=2000)]
    all_tweets = b24_all_tweets + db_tweets

    clean_tweets = list(filter(None, [clean_tweet(t, as_string=False) for t in all_tweets]))
    print('Clean tweets:', len(clean_tweets))
    documents = get_documents(clean_tweets)
    model = Doc2Vec(documents=documents, dm=1, size=200, window=10, min_count=10)

    document_vectors = {}
    for ctr, t in enumerate(b24_all_tweets):
        document_vectors[t] = model.docvecs[ctr]

    joblib.dump(document_vectors, 'src/NLP/junk/testing_on_brand24/data/document_vectors.pkl')


def cluster_tweets():
    all_tweets = get_b24_tweets()
    document_vectors = joblib.load('src/NLP/junk/testing_on_brand24/data/document_vectors.pkl')
    document_vectors_values = list(document_vectors.values())
    n_clusters = 10
    k_means = KMeans(n_clusters=n_clusters)
    k_means.fit(document_vectors_values)
    labels = list(k_means.labels_)

    clusters = {}
    for ctr, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(all_tweets[ctr])
        else:
            clusters[label] = [all_tweets[ctr]]

    joblib.dump(clusters, 'src/NLP/junk/testing_on_brand24/data/doc2vec_clusters.pkl')


if __name__ == '__main__':
    #run_d2v()
    cluster_tweets()
    get_accuracy('src/NLP/junk/testing_on_brand24/data/doc2vec_clusters.pkl')

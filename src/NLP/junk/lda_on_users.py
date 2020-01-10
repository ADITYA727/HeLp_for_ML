import os
import sys
import gensim
from gensim import corpora

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../../')
from src.NLP.similarity import get_data

Lda = gensim.models.ldamodel.LdaModel

def run_lda_on_all_tweets():
    user_tweets, users_retweets_count, all_retweet_count = get_data(length=1500)
    doc_clean = [text.split() for text in user_tweets.values()]
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

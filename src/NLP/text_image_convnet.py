import os, sys
import re, tqdm, joblib
import numpy as np
import lda
from multiprocessing import Process
import multiprocessing
# from ekphrasis.classes.preprocessor import TextPreProcessor
# from ekphrasis.classes.tokenizer import SocialTokenizer
# from ekphrasis.dicts.emoticons import emoticons
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn import pipeline
from keras.layers import Dense
from keras import backend as K
import tensorflow as tf
import splitter

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.NLP.preprocessing import clean_tweet
from src.mysql_utils import MySqlUtils
from nltk.corpus import stopwords

stops = set(stopwords.words('english'))

sql = MySqlUtils()
m = multiprocessing.Manager()
vect_queue = m.Queue()
corpus_list = m.list()


def lda_model(text_list):
    text1 = ''.join([text for text in text_list])
    text = text1.split()

    topic_data = {}
    cvectorizer = CountVectorizer(max_features=10000, stop_words=stops)
    cvz = cvectorizer.fit_transform(text)

    n_topics = 10
    n_iter = 70
    lda_model = lda.LDA(n_topics=n_topics, n_iter=n_iter)
    X_topics = lda_model.fit_transform(cvz)

    n_top_words = 10
    topic_summaries = []

    topic_word = lda_model.topic_word_  # get the topic words
    vocab = cvectorizer.get_feature_names()
    topic_dist = topic_word[0]
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
    topic_summaries.append(' '.join(topic_words))
    # print('Topic: {}'.format( ' '.join(topic_words)))
    return ' '.join(topic_words)


"""
def tokenize_hashtags(hashtags):
    text_processor = TextPreProcessor(
        # terms that will be normalized
        normalize=['url', 'email', 'percent', 'money', 'phone', 'user',
                   'time', 'url', 'date', 'number'],
        # terms that will be annotated
        annotate={"hashtag", "allcaps", "elongated", "repeated",
                  'emphasis', 'censored'},
        fix_html=True,  # fix HTML tokens

        # corpus from which the word statistics are going to be used
        # for word segmentation
        segmenter="twitter",

        # corpus from which the word statistics are going to be used
        # for spell correction
        corrector="twitter",

        unpack_hashtags=True,  # perform word segmentation on hashtags
        unpack_contractions=True,  # Unpack contractions (can't -> can not)
        spell_correct_elong=False,  # spell correction for elongated words

        # select a tokenizer. You can use SocialTokenizer, or pass your own
        # the tokenizer, should take as input a string and return a list of tokens
        tokenizer=SocialTokenizer(lowercase=True).tokenize,

        # list of dictionaries, for replacing tokens extracted from the text,
        # with other expressions. You can pass more than one dictionaries.
        dicts=[emoticons]
    )
    try:
        hashtags_text=text_processor.pre_process_doc(hashtags)
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', hashtags_text)
        return cleantext.replace('  ','')
    except Exception as e:
        print(e)
        return ''
"""


def initialize_words():
    content = None
    with open(home + '/../../data/word_list.txt') as f:  # A file containing common english words
        content = f.readlines()
    return [word.rstrip('\n') for word in content]


def parse_sentence(sentence, wordlist):
    new_sentence = ""  # output
    terms = sentence.split(' ')
    for term in terms:
        if term[0] == '#':  # this is a hashtag, parse it
            new_sentence += parse_tag(term, wordlist)
        else:  # Just append the word
            new_sentence += term
        new_sentence += " "

    return new_sentence


def parse_tag(term, wordlist):
    words = []
    # Remove hashtag, split by dash
    tags = term[1:].split('-')
    for tag in tags:
        word = find_word(tag, wordlist)
        while word != None and len(tag) > 0:
            words.append(word)
            if len(tag) == len(word):  # Special case for when eating rest of word
                break
            tag = tag[len(word):]
            word = find_word(tag, wordlist)
    return " ".join(words)


def find_word(token, wordlist):
    i = len(token) + 1
    while i > 1:
        i -= 1
        if token[:i] in wordlist:
            return token[:i]
    return None


def get_hashtag_tokenize(hash_tag):
    hashtag = hash_tag
    hash_tag = hash_tag.replace('#', '')
    hash_tag = ' '.join(hash_tag.split())
    if len(hash_tag) > 0:
        hashtag = splitter.split(hashtag)
        hashtag = ' '.join(word for word in hashtag)
        if len(hashtag) > 1:
            wordlist = initialize_words()
            return parse_sentence(hashtag, wordlist)

        else:
            return hash_tag.lower()
            # wordlist = initialize_words()
            # return parse_sentence(hashtag, wordlist)
    else:
        return hash_tag


def get_related_content(user):
    if user['related_content']:
        user['related_content'] = list(clean_tweet(user['related_content']))
        try:
            related_content = lda_model(user['related_content'])
        except Exception as e:
            print(e)
            return ''
    else:
        related_content = ''
    return related_content


def get_corpus(user_data):
    corpus = dict()
    corpus['user_handle'] = [user_data[0]['user_handle']]
    user_handle=user_data[0]['user_handle']
    corpus['tweet'] = []
    corpus['hashtags'] = []
    corpus['related_content'] = []
    tweet = clean_tweet(user_data[0]['text'])
    hashtags = get_hashtag_tokenize(user_data[0]['hashtags'])
    related_content = get_related_content(user_data[0])
    for user in tqdm.tqdm(user_data[1:]):
        if user['user_handle'] != user_handle:
            user_handle=user['user_handle']
            corpus['user_handle'].append(user['user_handle'])
            hashtags = ' '.join(word for word in hashtags.split())
            related_content = ' '.join(word for word in related_content.split())
            corpus['tweet'].append(tweet)
            corpus['hashtags'].append(hashtags)
            corpus['related_content'].append(related_content)
            tweet = clean_tweet(user['text'])
            hashtags = get_hashtag_tokenize(user['hashtags'])
            related_content = get_related_content(user)
        else:
            tweet = tweet + ' ' + clean_tweet(user['text'])
            hashtags = hashtags + ' ' + get_hashtag_tokenize(user['hashtags'])
            related_content = related_content + get_related_content(user)

    hashtags = ' '.join(word for word in hashtags.split())
    related_content = ' '.join(word for word in related_content.split())
    corpus['tweet'].append(tweet)
    corpus['hashtags'].append(hashtags)
    corpus['related_content'].append(related_content)
    corpus_list.append(corpus)


def vectorize_corpus(corpus, lsa=0, name=None):
    """
    :param corpus:
    :param lsa:
    :return:
    """
    print("inside_vectorizer")
    # Using sklearn's tfidfvectorizer to construct tfidf matrix
    print('tfidfvetorizer')
    vectorizer = TfidfVectorizer(max_features=10000, stop_words=stops)

    vector_matrix = vectorizer.fit_transform(corpus[0])
    # applied lsa and svd
    if lsa:
        svd = TruncatedSVD(100)
        lsa = pipeline.make_pipeline(svd, Normalizer(copy=False))
        vector_matrix = lsa.fit_transform(vector_matrix)
    vect_queue.put({name: vector_matrix})
    print('finished vectorizer')


def get_result():
    results = {}
    while not vect_queue.empty():
        results.update(vect_queue.get())
    return results


def mutiprocess_get_corpus(user_data):
    data = []
    data.append(user_data[:90001])
    data.append(user_data[90001:180110])
    data.append(user_data[180110:270381])
    data.append(user_data[270381:])
    """
    data.append(user_data[:200])
    data.append(user_data[200:400])
    data.append(user_data[400:600])
    data.append(user_data[600:800])
    data.append(user_data[800:1000])
    """

    jobs = []
    for i in range(len(data)):
        process = multiprocessing.Process(target=get_corpus, args=((data[i],)))
        jobs.append(process)
    for process in jobs:
        process.start()
    for process in jobs:
        process.join()

    corpus = corpus_list[0]
    print('making corpus')
    for data in corpus_list[1:]:
        corpus['user_handle'].extend(data['user_handle'])
        corpus['tweet'].extend(data['tweet'])
        corpus['hashtags'].extend(data['hashtags'])
        corpus['related_content'].extend(data['related_content'])
    return corpus


def multiprocessing_for_vectorizer_matrix(corpus):
    jobs = []
    content = ['tweet','hashtags','related_content']

    for name in content:
            process1 = multiprocessing.Process(target=vectorize_corpus, args=((corpus[name],), 0, name))
            jobs.append(process1)
    for process1 in jobs:
        process1.start()

    for process1 in jobs:
        process1.join()

def main():
    user_data = joblib.load(home + '/../../data/user_data.txt')
    print('user_data')
    corpus = mutiprocess_get_corpus(user_data)
    print("dumping corpus")
    joblib.dump(corpus, home + '/../../data/corpus.txt')
    multiprocessing_for_vectorizer_matrix(corpus)
    results= get_result()
    print('get_final_matrix')
    joblib.dump(results, home+'/../../data/results.txt')
main()
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os,sys,tqdm
import lda
from sklearn.cluster.k_means_ import KMeans
from collections import Counter
from gensim.models.keyedvectors import KeyedVectors
from gensim.models.word2vec import Word2Vec
import networkx as nx
import numpy as np
home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.NLP.preprocessing import clean_tweet
from src.mysql_utils import MySqlUtils
from nltk.corpus import stopwords
import warnings
warnings.filterwarnings("ignore")
stops = set(stopwords.words('english'))
a=''
sql = MySqlUtils()
threshold=0.7

def get_dataframe():
    user_data = joblib.load(home + '/../../data/user_data.txt')
    data=pd.DataFrame(list(user_data))
    return data

def lda_model(text_list):
    #text1 = ''.join([text for text in text_list])
    text = text_list.split()

    topic_data = {}
    cvectorizer = CountVectorizer(max_features=1000, stop_words=stops)
    cvz = cvectorizer.fit_transform(text)
    n_topics = 10
    n_iter = 70
    lda_model = lda.LDA(n_topics=n_topics, n_iter=n_iter)
    lda_model.fit_transform(cvz)

    n_top_words = 30
    topic_summaries = []

    topic_word = lda_model.topic_word_  # get the topic words
    vocab = cvectorizer.get_feature_names()
    topic_dist = topic_word[0]
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
    topic_summaries.append(' '.join(topic_words))
    # print('Topic: {}'.format( ' '.join(topic_words)))
    return ' '.join(topic_words)

def get_clusters(matrix):
    """Using sklearn's cosine_similarty to calculate cosine similarity between all documents


    :param matrix:
    :param corpus:
    :return:
    """
    cos_sim_matrix = cosine_similarity(matrix)
    # Using sklearn's cosine_similarty to calculate cosine similarity between all documents
    print("Matrix Mean: {}".format(cos_sim_matrix.mean()))
    print("variance")
    mat = np.where(cos_sim_matrix > threshold, 1, 0)
    # Get clusters using networkx
    network = nx.from_numpy_matrix(mat)
    clusters = list(nx.connected_components(network))
    # clusters contains indexes of users in corpus dictionary.
    """
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
    """
    return clusters, cos_sim_matrix
def vectorize_corpus(corpus):
    """
    :param corpus:
    :param lsa:
    :return:
    """
    # Using sklearn's tfidfvectorizer to construct tfidf matrix
    vectorizer = TfidfVectorizer(stop_words=stops)
    vector_matrix = vectorizer.fit_transform(corpus)
    return vector_matrix

def remove_hash(txt):
    return ' '.join(word for word in txt.split(' ') if not word.startswith('#') and  not word.startswith('@'))

def get_combined_tweet_data(data):
    tweet_data=list(data['text'])
    #hashtags=joblib.load(home+'/../../data/hashtags.txt')
    related_content=list(data['related_content'])
    twt_data=[]
    for i in range(len(tweet_data)):
        if related_content[i] and not related_content[i].isspace():
            try:
                r_content = lda_model(related_content[i])
            except Exception as e:
                print(e)
                a=related_content[i]
                print(a)
                r_content=''
        else:
            r_content = ''
        twt_data.append(r_content + tweet_data[i])
    return twt_data

def get_vector(data):
    tweet_data=get_combined_tweet_data(data)
    tweet_data = [clean_tweet(remove_hash(tweet)) for tweet in tweet_data]
    tweet=[tweet.split() for tweet in tweet_data]
    model=Word2Vec(min_count=1)
    model.build_vocab(tweet)
    model.train(tweet,total_examples=model.corpus_count, epochs=model.iter)
    final_matrix=[]
    count=[]

    for index, tweet in tqdm.tqdm(enumerate(tweet)):
        if tweet :
            matrix=[model[text] for text in tweet if text]
            matrix = np.array(matrix)
            final_matrix.append(np.mean(matrix,axis=0))
        else:
            count.append(index)
    return np.array(final_matrix), count, tweet_data

def get_cluster_kmeans(count):
    for n,index in enumerate(count):
        user_handle.pop(index-n)
        tweet_data.pop(index-n)
    zipped = zip(clus.labels_, tweet_data, user_handle)
    cluster_data=sorted(zipped, key= lambda x:x[0])
    count=0
    users=[]
    users_cluster=[]
    tweet_topic=[]
    text = ''
    for cluster in cluster_data:
        if count== cluster[0]:
            text=text+cluster[1]
            users.append(cluster[2])
        else:
            tweet_topic.append(lda_model(text))
            users_cluster.append(users)
            users=[]
            count = count + 1
            #for new users
            users.append(cluster[2])
            text = cluster[1]

    tweet_topic.append(lda_model(text))
    return cluster_data, tweet_topic, users_cluster

print('getting dataframe')
data=get_dataframe()
user_handle=list(data['user_handle'])
print('getting final matrix')
final_matrix, count, tweet_data=get_vector(data)
joblib.dump(final_matrix, home + '/../../data/final_matrix.txt')
print('Applying clustering')
sse=dict()
for k in range(1,25):
    kmeans = KMeans(n_clusters=k, max_iter=100, random_state=0)
    clus=kmeans.fit(final_matrix)
    sse[k]=clus.inertia_
print('20 clusters are ready')
cluster_data, tweet_topic, users_cluster = get_cluster_kmeans(count)
joblib.dump(tweet_topic, home + '/../../data/tweet_topic.txt')
joblib.dump(users_cluster, home + '/../../data/users_cluster.txt')
joblib.dump(sse, home + '/../../data/sse.txt')




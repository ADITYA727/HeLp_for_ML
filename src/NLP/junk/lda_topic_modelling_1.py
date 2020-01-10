# -*- coding: utf-8 -*-
import pandas as pd
import preprocessor as p
import re

import warnings
warnings.filterwarnings("ignore")

output_file_base_loc='/home/stealthuser/Perosnal/Sentimental/15_july/Prototype/tweet_sentiment/'
data=pd.read_csv(output_file_base_loc+'extremely positive.csv')


# compile documents
doc_complete = list(data['text'])

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def cleaning_sentence(sentence):
	stop_free = " ".join([i for i in sentence.lower().split() if i not in stop])
	hashtag_value = p.parse(stop_free).hashtags
	sentence = p.clean(stop_free)	
	sentence = re.sub("[^A-Za-z .]+","", sentence)
	normalized = " ".join(lemma.lemmatize(word) for word in sentence.split())
	return normalized


# def clean(doc):
#     stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
#     punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
#     normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
#     return normalized


doc_clean = [cleaning_sentence(doc).split() for doc in doc_complete]       


print("Document cleaning is done...")

import gensim
from gensim import corpora

dictionary = corpora.Dictionary(doc_clean)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
Lda = gensim.models.ldamodel.LdaModel

# Number of Topics – Number of topics to be extracted from the corpus. 
# Researchers have developed approaches to obtain an optimal number of topics by using Kullback Leibler Divergence Score.

# Number of Topic Terms – Number of terms composed in a single topic. 
# It is generally decided according to the requirement.
# If the problem statement talks about extracting themes or concepts, it is recommended to choose a higher number, 
# if problem statement talks about extracting features or terms, a low number is recommended.

# Number of Iterations / passes – Maximum number of iterations allowed to LDA algorithm for convergence.


ldamodel = Lda(doc_term_matrix, num_topics=10, id2word = dictionary, passes=70)

f=open(output_file_base_loc+'extremely positive_topics.txt','w')

f.write(str(ldamodel.print_topics(num_topics=10, num_words=4)))


# print(ldamodel.print_topics(num_topics=10, num_words=4))
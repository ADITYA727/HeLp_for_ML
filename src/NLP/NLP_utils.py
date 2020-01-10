
import nltk
from nltk.collocations import *
import collections
import sys, os
# Make sure you put the mitielib folder into the python search path.  There are
# a lot of ways to do this, here we do it programmatically with the following
# two statements:
parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent + '/../../lib/MITIE/mitielib')
from mitie import named_entity_extractor, tokenize

def get_trigrams(text, count):
    #bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()

    # change this to read in your data
    #finder1 = BigramCollocationFinder.from_words(text.split(' '))
    finder2 = TrigramCollocationFinder.from_words(text.split(' '))

    # only bigrams that appear 3+ times
    #finder1.apply_freq_filter(2)
    tri_gram_list = []
    for i in range(3,4):
        finder2.apply_freq_filter(i)

        # return the 10 n-grams with the highest PMI
        # items = finder1.nbest(bigram_measures.pmi, 35)
        # for item in items:
        #     print(' '.join(item))
        items = finder2.nbest(trigram_measures.pmi, count)
        for item in items:
            tri_gram_list.append(' '.join(item))
    return tri_gram_list

def get_unigrams(text, count):
    wordcount = collections.Counter()


    for word in text.split(' '):
        if word not in wordcount:
            wordcount[word] = 1
        else:
            wordcount[word] += 1
    return wordcount.most_common(count)


def get_entities(text, count):
    ner = named_entity_extractor(parent + '/../../lib/MITIE/MITIE-models/english/ner_model.dat')
    # Load a text file and convert it into a list of words.
    tokens = tokenize(text)

    entities = ner.extract_entities(tokens)
    entity_count = collections.Counter()

    for e in entities:
        range = e[0]
        entity_text = " ".join(tokens[i].decode() for i in range)
        if entity_text not in entity_count:
            entity_count[entity_text] = 1
        else:
            entity_count[entity_text] += 1
    return entity_count.most_common(count)

import spacy
from nltk import Tree
from collections import defaultdict
import json
import os
import gensim

home=os.path.abspath(os.path.dirname(__file__))

input_filename = home+'/../../data/reviews_Cell_Phones_and_Accessories_5.json'
output_filename = home+'/../../data/reviews_Cell_Phones_and_Accessories_5.tsv'
np_filename = home+'/../../data/np.tsv'


model = gensim.models.KeyedVectors.load_word2vec_format(home+'/../../lib/GoogleNews-vectors-negative300-slim.bin', binary=True, unicode_errors='ignore')

nlp = spacy.load('en')


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


inf = open(input_filename, 'r')
of = open(output_filename, 'w')
npf = open(np_filename, 'w')

count = 0
for count, line in enumerate(inf.readlines()):
    try:
        outdict = defaultdict(list)
        json_text = json.loads(line)
        doc = nlp(json_text['reviewText'])
        for sent in doc.sents:
            #print(to_nltk_tree(sent.root).pretty_print())
            outdict['reviewer_id'] = json_text['reviewerID']
            for tok in sent:
                if tok.tag_=='JJ':
                    outdict['adj_list'].append(str(tok))
            for np in sent.noun_chunks:
                of.write('{}\n'.format(np))
                outdict['noun_list'].append(str(np))
                for item in np.split(' '):
                    vector = vector + model[item]
        outdict['vector'] = vector.dumps()
        of.write('{}\n'.format(json.dumps(outdict)))
    except:
        pass


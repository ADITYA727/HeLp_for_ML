#!/usr/bin/python
#
# This example shows how to use the MITIE Python API to perform named entity
# recognition and also how to run a binary relation detector on top of the
# named entity recognition outputs.
#
from mitie import *
from collections import defaultdict


print("loading NER model...")
ner = named_entity_extractor('MITIE-models/english/ner_model.dat')
print("\nTags output by this NER model:", ner.get_possible_ner_tags())

# Load a text file and convert it into a list of words.
tokens = tokenize(load_entire_file('ArnabGswm.txt'))
#print("Tokenized input:", tokens)

entities = ner.extract_entities(tokens)
#print("\nEntities found:", entities)
#print("\nNumber of entities detected:", len(set(entities)))
text_entities = []
for e in entities:
    range = e[0]
    entity_text = " ".join(tokens[i].decode() for i in range)
    text_entities.append(entity_text)
print(text_entities)


import spacy
from nltk import Tree
#https://explosion.ai/blog/displacy-js-nlp-visualizer

nlp = spacy.load('en')
doc = nlp(u"Modi's Permanent Ambassador @SrBachchan for GST must quit India gracefully &amp; settle in Panama Paradise #ParadisePapers")

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


[to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]

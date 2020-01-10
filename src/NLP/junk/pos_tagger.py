# -*- coding: utf-8 -*-
import nltk
from nltk.util import ngrams
from nltk import word_tokenize
# https://pypi.python.org/pypi/tweet-preprocessor/0.4.0
import preprocessor as p
import re
# p.set_options(p.OPT.URL, p.OPT.EMOJI,p.OPT.SMILEY)

from nltk import tokenize
# paragraph = "It was one of the worst movies I've seen, despite good reviews. Unbelievably bad acting!! Poor direction. VERY poor production. The movie was bad. Very bad movie. VERY BAD movie!"
# sentence_list = tokenize.sent_tokenize(paragraph)

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
# import codecs

s="Demonetisation helps in removing black money"

# s="he helped in building play ground."

import warnings
warnings.filterwarnings("ignore")

# s="I don't know about poor , but I am sure your lutyen family is surely dying. But its sad your looted money has been burnt by #Demonetisation https:// twitter.com/OfficeOfRG/sta tus/813979312252563456 ‚Ä¶"
sentence_list = tokenize.sent_tokenize(s)
# s.encode('utf-8')

def cleaning_sentence(sentence):
	hashtag_value = p.parse(sentence).hashtags
	sentence = p.clean(sentence)	
	sentence = re.sub("[^A-Za-z .]+","", sentence)
	return sentence

for sentence in sentence_list:
	
	# cleansing step...
	sentence = cleaning_sentence(sentence)
	
	text = word_tokenize(sentence)
	y=list(ngrams(text,2))
	l=map(lambda x:' '.join(x),y)
	text.extend(l)
	print "#########################################################################################################"
	print sentence
	print "\n"
	print nltk.pos_tag(text)
	print "#########################################################################################################"
	print "\n\n"
from __future__ import division
from noun_phrases import get_noun_phrases
import pandas as pd
import os
import calendar
import warnings
warnings.filterwarnings("ignore")
from collections import Counter
import re
from nltk import word_tokenize
import calendar
import multiprocessing
from multiprocessing import Pool
import matplotlib.pyplot as plt
#from wordcloud import WordCloud
from wordcloud import WordCloud, STOPWORDS

# STOPWORDS = STOPWORDS.union(more_stopwords)

def words(text): return re.findall(r'\w+', text.lower())

def get_noun_freq(combined_tweet):
	# word_freq = Counter(words(combined_tweet))	
	# word_list = words(combined_tweet)
	# tagging = nltk.pos_tag(word_list)
	# nouns = [word for word,pos in tagging if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
	# noun_freq = Counter(nouns)
	# frequent_nouns={}
	# print combined_tweet
	nouns= get_noun_phrases(combined_tweet)
	return nouns
	# noun_freq=Counter(nouns)
	# return noun_freq
	# return noun_freq.most_common(5)

# for file in files:
def boom_boom(file):
	print file[:-4]
	print "______________"
	print "\n\n"
	more_stopwords = {'hardikpatel':'','#hardikpatel':'','#anandibenpatel':'','hardik':'','hardik patel':'','#shivsena':''}
	rep = dict((re.escape(k), v) for k, v in more_stopwords.iteritems())
	pattern = re.compile("|".join(rep.keys()))
	
	output_file_base_loc='/home/stealthuser/Perosnal/Sentimental/Patel_Reservation/Output_csvs/'
	# d=pd.read_csv(output_file_base_loc+'patel_reservation_final.csv')
	# files=['positive.csv','negative.csv']
	years=[2015,2016,2017]
	d=pd.read_csv(output_file_base_loc+file)
	final_dir=output_file_base_loc+file[:-4]+'_topic_modelling'+'/'
	if os.path.exists(final_dir):
		pass
	else:
		os.mkdir(final_dir)
	for year in years:
		print year
		print "\n"
		# d+'_'+str(year)=d[d['year']==year]
		# d+'_'+str(year).to_csv(output_file_base_loc+'year_'+str(year)+'.csv')
		x=d[d['year']==year]
		# x.to_csv(output_file_base_loc+'year_'+str(year)+'.csv')
		# months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
		# dif_months= list(x['month'].unique())	
		# combined_tweet_yearly=' . '.join(x['cleaned_text'])
		noun_list=[]
		for index,tweet in enumerate(x['cleaned_text']):
			# print index
			
			tweet = pattern.sub(lambda m: rep[re.escape(m.group(0))], tweet)
			
			# tweet = 
			noun_list.extend(get_noun_freq(tweet))
		print "****************************************************************************************************"
		noun_freq=Counter(noun_list)
		print dict(noun_freq)
		print "****************************************************************************************************"
		print "\n\n"
		# topic_frequency_dict = get_noun_freq(combined_tweet_yearly)
		# print topic_frequency_dict
		

		# print noun_freq
		wordcloud = WordCloud(stopwords=STOPWORDS,
                          background_color='white',
                          width=1200,
                          height=1000
                         ).generate_from_frequencies(dict(noun_freq))
		plt.imshow(wordcloud)
		plt.axis('off')
		# plt.show()
		year_dir=final_dir+str(year)+'/'
		if os.path.exists(year_dir):
			# print "Existing "+year_dir
			pass
		else:
			# print "Making "+year_dir
			os.mkdir(year_dir)

		plt.savefig(year_dir+str(year)+'_'+file[:-4]+'_cloud'+'.png')
		
file_to_use=['positive.csv','negative.csv']
pool=Pool(processes=2)
pool.map(boom_boom,file_to_use)
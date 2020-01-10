import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import re
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import csv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import preprocessor as p
import multiprocessing
from multiprocessing import Pool
import os
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from textblob import TextBlob
# lemma = WordNetLemmatizer()
# stop = set(stopwords.words('english'))

# add_stop=['http','u','s']
# stop = stop.union(add_stop)

# def cleaning_sentence(sentence):
# 	p.set_options(p.OPT.URL)	
# 	#hashtag_value = p.parse(stop_free).hashtags
# 	sentence=str(sentence)
# 	sentence = p.clean(sentence)	
# 	reg_http=r"(http)(s)?(://)?"
# 	sentence = re.sub(reg_http,"", sentence)

# 	stop_free = " ".join([i for i in sentence.lower().split() if i not in stop])
# 	sentence = re.sub("[^A-Za-z .#]+","", stop_free)
	
# 	#normalized = " ".join(lemma.lemmatize(word) for word in sentence.split())
# 	return sentence
def url_check(url):
	url=str(url)
	if (url.split(":")[0]=='https'):
		return True
	else:
		return False

def func(file):
	analyzer = SentimentIntensityAnalyzer()

	# input_file_loc='/home/stealthuser/Perosnal/Sentimental/Patel_Reservation/Output_csvs/'+'patel_reservation_final.csv'
	output_file_loc='/home/stealthuser/Perosnal/Sentimental/Patel_Reservation/Output_csvs/'
	# data = pd.read_csv(input_file_loc)
	# labels=['negative','neutral','positive']


	# for label in labels:
	temp=pd.read_csv(output_file_loc+file)
	temp=temp[1500:]
	f=open(output_file_loc+file[:-4]+'_'+'reply.csv','a')
	# wr=csv.writer(f)
	f.write("Tweet_Replies"+'\n')
	for index,url in enumerate(temp['permalink']):
		print file
		print index
		status=url_check(url)
		if(status):
			res=requests.get(str(url))
			scrap=res.text
			to_search='class=\"TweetTextSize'
			positions = [m.start() for m in re.finditer(to_search,scrap)]				
	 		if(positions):
		 		for position in positions:
		 			i=0
		 			j=0
		 			for i in range(position+20,len(scrap)):
		 				if(scrap[i]=='>'):
		 					j=i
		 					break
		 			if(i!=0 and j!=0):
			 			reply_op=''
			 			while(scrap[j+1]!='<'):
			 				j+=1
			 				reply_op+=scrap[j]
			 			f.write(reply_op+'\n')
	f.close()
	# replies=pd.read_csv(output_file_loc+file[:-4]+'_'+'reply.csv',low_memory=False,error_bad_lines=False)
	# replies['cleaned_text']=''
	# score_column = ['positive','negative','neutral']
	# for column in score_column:
	# 	replies[column] = 0 
	# for index,tweet in enumerate(replies['Tweet_Replies']):
	# 	print index
	# 	cleaned_text=cleaning_sentence(tweet)
	# 	score = analyzer.polarity_scores(cleaned_text)
	# 	replies.ix[index,'positive']=score['pos']
	# 	replies.ix[index,'negative']=score['neg']
	# 	replies.ix[index,'neutral']=score['neu']
	# 	replies.ix[index,'compound']=score['compound']
	# en_beg=-1
	# en_end=-0.6

	# #neg_beg=-0.6
	# neg_end=-0.1


	# #neu_beg=-0.2
	# neu_end=0.1

	# #pos_beg=0.2
	# pos_end=0.6

	# #ep_beg=0.6
	# ep_end=1


	# # scale=[en_beg,en_end,neg_end,neu_end,pos_end,ep_end]

	# # labels=['extremly negative','negative','neutral','positive','extremely positive']

	# scale=[en_beg,neg_end,neu_end,ep_end]

	# labels=['negative','neutral','positive']

	# replies['classification']= pd.cut(replies['compound'], bins = scale,labels=labels,include_lowest=True)
	# replies.to_csv(output_file_loc+file[:-4]+'_'+'reply_sentiment.csv')

file_to_use=['positive.csv','negative.csv','neutral.csv']
pool=Pool(processes=3)
pool.map(func,file_to_use)

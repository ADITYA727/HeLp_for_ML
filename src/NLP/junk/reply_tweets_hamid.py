# -*- coding: utf-8 -*-
import pandas as pd
from classification_tweet import classification_tweet
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from twarc import Twarc
import urllib3
import os
import config_path as c_p
import config_1 as c1
import config_2 as c2
import config_3 as c3
import config_4 as c4
import config_7 as c7
import config_8 as c8
import config_9 as c9
import config_10 as c10

import multiprocessing
from multiprocessing import Pool

urllib3.disable_warnings()

# consumer_key = 'inveFLfT9YY0lnVftUqpMsgld'
# consumer_secret = 'nhV69AveRBQTgSPhWfmZ3lUuZsSQE6xeLmM8E7sMOwHV9X8SgW'
# access_token = '1860637417-KzRl3BGiYHaF5fxBGxK17PjR99YV197sfldyTFS'
# access_token_secret = 'WFmLHNEnlV2Ja5mdjanWwVx7lbq6I0DoaTiLJlBODLvfJ'

# t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)

import datetime
# today = datetime.date.today()
# margin = datetime.timedelta(days = 7)


# base_dir='/home/stealthuser/Perosnal/Sentimental/12 august/Data/Hamid output csvs/'

# output_dir = base_dir+'reply/'

def f(file):
	print file
	today = datetime.date.today()
	margin = datetime.timedelta(days = 7)
	analyzer = SentimentIntensityAnalyzer()
	acess_changer = [c8,c9,c10,c7,c1,c2,c3,c4]
	
	# base_dir='/home/stealthuser/Perosnal/Sentimental/12 august/Data/Hamid output csvs/'
	base_dir = c_p.input_csv_path
	if os.path.exists(base_dir+'reply/'):
		output_dir = base_dir+'reply/'
		pass
	else:
		os.mkdir(base_dir+'reply/')
		output_dir = base_dir+'reply/'
	
	data=pd.read_csv(base_dir+file,low_memory=False,error_bad_lines=False)
	data['reply']=''
	reply=[]
	acess_changer_counter = 0
	max_tweet=35
	config_key=0
	for index,tweet in enumerate(data['text']):
		print file +  " "+str(index)
		t_id = data.ix[index,'permalink'].split('/')[-1:][0]
		tweet_date = data.ix[index,'date'].split()[0]
		
		if (acess_changer_counter%max_tweet == 0):
			access_point = acess_changer[config_key%len(acess_changer)]
			config_key+=1
			t = Twarc(access_point.consumer_key, access_point.consumer_secret, access_point.access_token, access_point.access_token_secret)
		
		acess_changer_counter+=1
		print access_point							
		tweet_r = t.tweet(t_id)
		if(len(tweet_r)>0):
			reply_tweets = []
			req_format_date = tuple(map(lambda x:int(x),tweet_date.split('-')))
			if (today - margin <= datetime.date(req_format_date[0],req_format_date[1],req_format_date[2]) ):
				for reply_tweet in t.replies(tweet_r):
					reply.append(reply_tweet['text'].encode('utf-8'))
					# print reply_tweet['text'].encode('utf-8')
					reply_tweets.append(reply_tweet['text'].encode('utf-8'))
			# delimiter for replies is '==<>=='
			
			data.ix[index,'reply'] = '==<>=='.join(reply_tweets)
	df_reply_comment = pd.DataFrame({'replies':reply})
	
	for index_comment,reply in enumerate(df_reply_comment['replies']):
		score = analyzer.polarity_scores(str(reply))
		df_reply_comment.ix[index_comment,'positive']=score['pos']
		df_reply_comment.ix[index_comment,'negative']=score['neg']
		df_reply_comment.ix[index_comment,'neutral']=score['neu']
		df_reply_comment.ix[index_comment,'compound']=score['compound']

	# df_reply_comment.to_csv(output_dir+file[:-4]+'_replies_sentiment.csv')
	data.to_csv(output_dir+file[:-4]+'_comments.csv')
	status,paths_reply_label = classification_tweet(df_reply_comment,output_dir,file[:-4])

if __name__ == '__main__':
	# file_to_use = ['negative.csv','positive.csv','neutral.csv']
	file_to_use = c_p.file_to_use
	pool=Pool(processes=3)

	# for file in file_to_use:
	pool.map(f,file_to_use)
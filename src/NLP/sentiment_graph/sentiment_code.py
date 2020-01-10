from __future__ import division
import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# files reading into DATAFRAMES....
input_file_loc = '/home/stealthuser/Perosnal/Sentimental/Odisha/Twitter/GetOldTweets-python-master/output_csv/'

tweet_files=os.listdir(input_file_loc)

dfs=[]
for file in tweet_files:
	dfs.append(pd.read_csv(input_file_loc+file,low_memory=False,error_bad_lines=False,sep=';'))

# data_tweet= pd.concat(dfs[1:], ignore_index=True)

data_tweet= pd.concat(dfs, ignore_index=True)

data_tweet = data_tweet.drop_duplicates('text')

data_tweet=data_tweet.reset_index()
del data_tweet['index']

print(data_tweet.shape)

output_file_base_loc='/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/'

if os.path.exists(output_file_base_loc):
	pass
else:
	os.mkdir(output_file_base_loc)
	print "Made"

output_file_loc = output_file_base_loc+'output_general_sentiment.csv'
analyzer = SentimentIntensityAnalyzer()

# op_data = data_tweet.filter(['username','date','text','id','permalink','hashtags'],axis=1)
op_data = data_tweet
score_column = ['positive','negative','neutral','compound','cleaned_positive','cleaned_negative','cleaned_neutral','cleaned_compound']
for column in score_column:
	op_data[column] = 0 

op_data['cleaned_text']=''
op_data['year']=''
op_data['month']=''
op_data['day']=''


import pandas as pd
import preprocessor as p

import re
import os
import warnings
warnings.filterwarnings("ignore")
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
# from textblob import TextBlob

stop = set(stopwords.words('english'))

add_stop=['http','u','s']
stop = stop.union(add_stop)
# exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def cleaning_sentence(sentence):
	p.set_options(p.OPT.URL)	
	#hashtag_value = p.parse(stop_free).hashtags
	sentence=str(sentence)
	sentence = p.clean(sentence)	
	reg_http=r"(http)(s)?(://)?"
	sentence = re.sub(reg_http,"", sentence)
	stop_free = " ".join([i for i in sentence.lower().split() if i not in stop])
	sentence = re.sub("[^A-Za-z .#]+","", stop_free)
	#normalized = " ".join(lemma.lemmatize(word) for word in sentence.split())
	return sentence

for index,tweet in enumerate(op_data['text']):
	print index
	# print tweet
	op_data.ix[index,'year'],op_data.ix[index,'month'],op_data.ix[index,'day']=op_data.ix[index,'date'].split()[0].split('-')
	cleaned_tweet=cleaning_sentence(tweet)
	op_data.ix[index,'cleaned_text']=cleaned_tweet
	score = analyzer.polarity_scores(str(tweet))	
	score_cleaned = analyzer.polarity_scores(str(cleaned_tweet))
	op_data.ix[index,'cleaned_positive']=score_cleaned['pos']
	op_data.ix[index,'cleaned_negative']=score_cleaned['neg']
	op_data.ix[index,'cleaned_neutral']=score_cleaned['neu']
	op_data.ix[index,'cleaned_compound']=score_cleaned['compound']
	op_data.ix[index,'positive']=score['pos']
	op_data.ix[index,'negative']=score['neg']
	op_data.ix[index,'neutral']=score['neu']
	op_data.ix[index,'compound']=score['compound']

# defining scale 

en_beg = -1
en_end = -0.6

#neg_beg=-0.6
neg_end = -0.5

#neu_beg=-0.2
neu_end = 0.5

#pos_beg=0.2
pos_end = 0.6

#ep_beg=0.6
ep_end = 1


# scale=[en_beg,en_end,neg_end,neu_end,pos_end,ep_end]

# labels=['extremly negative','negative','neutral','positive','extremely positive']

scale = [en_beg,neg_end,neu_end,ep_end]

labels = ['negative','neutral','positive']

op_data['classification']= pd.cut(op_data['compound'], bins = scale,labels=labels,include_lowest=True)

for label in labels:
	print label
	classified_df=op_data[op_data['classification'] == label]
	# classified_df.sort(['compound'],ascending=False,inplace=True)
	# classified_df.sort([label],ascending=False,inplace=True)
	classified_df.to_csv(output_file_base_loc+label+'.csv')

op_data.to_csv(output_file_loc)

# extremly negative  ----->  (622, 12)
# negative  ----->  (1661, 12)
# neutral  ----->  (5211, 12)
# positive  ----->  (1494, 12)
# extremely positive  ----->  (607, 12)


# >>> x=pd.read_csv(output_file_base_loc+'positive.csv')
# >>> x.shape
# (1242, 17)
# >>> x=pd.read_csv(output_file_base_loc+'negative.csv')
# >>> 
# >>> x.shape
# (243, 17)
# >>> x=pd.read_csv(output_file_base_loc+'neutral.csv')
# >>> x.shape
# (3998, 17)
# >>> 
no_pos=op_data[op_data['classification']=='positive'].shape[0]
no_neg=op_data[op_data['classification']=='negative'].shape[0]
no_neu=op_data[op_data['classification']=='neutral'].shape[0]

no_tweets=op_data.shape[0]

print "No of tweets is: "+ str(no_tweets)
print "Percentage of Positive Tweets is: "+ str((no_pos/no_tweets)*100)+'%'
print "Percentage of Negative Tweets is: "+ str((no_neg/no_tweets)*100)+'%'
print "Percentage of Neutral Tweets is: "+ str((no_neu/no_tweets)*100)+'%'
# No of tweets is: 9714
# >>> print "Percentage of Positive Tweets is: "+ str((no_pos/no_tweets)*100)+'%'
# Percentage of Positive Tweets is: 10.8297302862%
# >>> print "Percentage of Negative Tweets is: "+ str((no_neg/no_tweets)*100)+'%'
# Percentage of Negative Tweets is: 0.916203417748%
# >>> print "Percentage of Neutral Tweets is: "+ str((no_neu/no_tweets)*100)+'%'
# Percentage of Neutral Tweets is: 88.2540662961%
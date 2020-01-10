from __future__ import division
import pandas as pd
# import config_path as cp

# file_to_use = ['negative.csv','positive.csv']
# file_to_use = cp.file_to_use

classification=['positive','negative','neutral']
# base_dir_reply=cp.input_csv_path+'reply/'

output_file_loc='/home/stealthuser/Perosnal/Sentimental/Patel_Reservation/Output_csvs/reply/'
file_to_use=['positive_reply_sentiment_classification.csv','negative_reply_sentiment_classification.csv','neutral_reply_sentiment_classification.csv']
stats_value={}
for file in file_to_use:
	percent_values=[]
	# file_to_read= output_file_loc+file[:-4]+'_tweet_reply_sentiment/'+file[:-4]+'_replies_sentiment_classification.csv'
	data=pd.read_csv(output_file_loc+file)
	
	for class_value in classification:
		x=data[data['classification']==class_value]
		print x.shape[0]
		print data.shape[0]
		percent_values.append((x.shape[0]/data.shape[0])*100)
	key='Percentage'+' '+file.split('_')[0]+' '+file.split('_')[1] 
	stats_value[key]=percent_values
	# stats_value={'Positive':,'negative':,'neutral':}
new_df=pd.DataFrame(stats_value)
new_classification=map(lambda x:x+' '+'tweets',classification)
new_df.index=new_classification	

new_df.to_csv(output_file_loc+'tweet_sentiment_stats.csv')
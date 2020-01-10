def classification_tweet(op_data,output_dir,f_name):
	import pandas as pd
	import os
	en_beg=-1
	en_end=-0.6

	#neg_beg=-0.6
	neg_end=-0.1


	#neu_beg=-0.2
	neu_end=0.1

	#pos_beg=0.2
	pos_end=0.6

	#ep_beg=0.6
	ep_end=1


	# scale=[en_beg,en_end,neg_end,neu_end,pos_end,ep_end]

	# labels=['extremly negative','negative','neutral','positive','extremely positive']

	scale=[en_beg,neg_end,neu_end,ep_end]

	labels=['negative','neutral','positive']

	op_data['classification']= pd.cut(op_data['compound'], bins = scale,labels = labels,include_lowest=True)
	paths_reply_label=[]
	final_dir=output_dir+f_name+'_tweet_reply_sentiment/'
	if os.path.exists(final_dir):
		pass
	else:
		os.mkdir(final_dir)
	for label in labels:
		print label
		classified_df = op_data[op_data['classification'] == label]
		# classified_df.sort(['compound'],ascending=False,inplace=True)
		classified_df.sort([label],ascending=False,inplace=True)
		classified_df.to_csv(final_dir+f_name+'_reply_'+label+'.csv')
		paths_reply_label.append(final_dir+f_name+'_reply_'+label+'.csv')
	op_data.to_csv(final_dir+f_name+'_replies_sentiment_classification.csv')
	return True,paths_reply_label
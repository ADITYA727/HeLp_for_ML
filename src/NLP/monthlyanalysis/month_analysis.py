from __future__ import division
import os
import calendar
import warnings
warnings.filterwarnings("ignore")


import pandas as pd
output_file_base_loc = '/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/'
d=pd.read_csv(output_file_base_loc+'output_general_sentiment.csv')
years=[2016,2017]

for year in years:
	print(year)
	# output_year_loc = output_file_base_loc+str(year)+'/'
	# if os.path.exists(output_year_loc):
	# 	pass
	# else:
	# 	os.mkdir(output_year_loc)
	# 	print "Made"
	# d+'_'+str(year)=d[d['year']==year]
	# d+'_'+str(year).to_csv(output_file_base_loc+'year_'+str(year)+'.csv')
	x=d[d['year']==year]
	# x.to_csv(output_file_base_loc+'year_'+str(year)+'.csv')
	dif_months= list(x['month'].unique())
	dict_stats={}
	pos=[]
	neg=[]
	neu=[]
	tweets=[]
	per_pos=[]
	per_neg=[]
	per_neu=[]
	for dif_month in dif_months:
		y=x[x['month']==dif_month]
		
		tweets.append(y.shape[0])
		pos.append(y[y['classification']=='positive'].shape[0])
		per_pos.append((y[y['classification']=='positive'].shape[0]/y.shape[0])*100)
		
		neg.append(y[y['classification']=='negative'].shape[0])
		per_neg.append((y[y['classification']=='negative'].shape[0]/y.shape[0])*100)
		
		neu.append(y[y['classification']=='neutral'].shape[0])
		per_neu.append((y[y['classification']=='neutral'].shape[0]/y.shape[0])*100)
	
	dict_stats['Total tweets']=tweets
	dict_stats['Positive Tweets']=pos
	dict_stats['Negative Tweets']=neg
	dict_stats['Neutral Tweets']=neu
	
	dict_stats['Positive Percentage']=per_pos
	dict_stats['Negative Percentage']=per_neg
	dict_stats['Neutral Percentage']=per_neu

	
	new_df = pd.DataFrame(dict_stats)
	month_names_list=[]
	for i in dif_months:
		 month_names_list.append(calendar.month_abbr[i])
	new_df.index = month_names_list
	new_df.to_csv(output_file_base_loc+'year_analysis/'+'year_'+str(year)+'_analysis'+'.csv')
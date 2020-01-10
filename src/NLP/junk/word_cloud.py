# word cloud program
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import os
import pandas as pd
import re
import preprocessor as p

more_stopwords = {'oh', 'will', 'hey', 'yet','html','au','du','la','atus','de','see','look','know','dont','new','say','pls','make','support','u','s','us','one','let','way','rt','since'}
STOPWORDS = STOPWORDS.union(more_stopwords)

input_file_base_loc='/home/stealthuser/Perosnal/Sentimental/22_july_17/Meghalaya/output_csv/'
output_file_base_loc='/home/stealthuser/Perosnal/Sentimental/22_july_17/Meghalaya/Word_cloud_images/'
files=os.listdir(input_file_base_loc)
for file in files:
	data=pd.read_csv(input_file_base_loc+file,low_memory=False,error_bad_lines=False)
	text=""
	#text=" ".join(list(data['cleaned_text']))
	for i in list(data['cleaned_text']):
		i_d=p.clean(str(i))
		text+=str(i_d)+" "
	wordcloud = WordCloud(stopwords=STOPWORDS,
	                          background_color='white',
	                          width=1200,
	                          height=1000
	                         ).generate(text)


	plt.imshow(wordcloud)
	plt.axis('off')
	# plt.show()

	plt.savefig(output_file_base_loc+file[:-3]+'jpeg')
	print "Done "+str(output_file_base_loc+file[:-3]+'jpeg')
'''
more_stopwords = {'oh', 'will', 'hey', 'yet', ...}
STOPWORDS = STOPWORDS.union(more_stopwords)


'''
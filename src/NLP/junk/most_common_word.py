from __future__ import with_statement
from collections import Counter
import os
import string 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

input_data = '/home/stealthuser/Perosnal/Sentimental/15_july/Prototype/speech_input/'
output_data ='/home/stealthuser/Perosnal/Sentimental/15_july/Prototype/speech_output/'
# os.chdir(input_data)


# files=os.listdir('.')

def remove_stopwords(list_data):
	import nltk
	from nltk.corpus import stopwords
	stop = set(stopwords.words('english'))
	import calendar
	month_name =list(calendar.month_name)
	month_name= map(lambda x:x.lower(),month_name)
	add_stop=['us','must','new','comes','without','would','want','say','can\'t','doesn\'t','cant','would','one']
	stop=stop.union(set(month_name+add_stop))
	# for i in stop:
	# 	if i in list_data:
	# 		list_data.remove(i)
	y= [word for word in list_data if word not in stop]
	return y

def data_preprocessing(data):
	data=data.lower()
	data=data.translate(None, string.punctuation)
	return data

for file in os.listdir(input_data):
	f=open(input_data+file,'r')
	#f=open('try_1.txt','r')
	data=f.read()
	data = data_preprocessing(data)
	list_data=data.split()
	# print "len: "+str(len(list_data))
	final_list_data =remove_stopwords(list_data)
	# print "len: "+str(len(final_list_data))
	data_dict = Counter(final_list_data)
	f_output = open(output_data+file,'w')
	# print data_dict.most_common(10)
	f_output.seek(0)
	f_output.write(str(data_dict.most_common(10)))
	f_output.close()
	f.close()
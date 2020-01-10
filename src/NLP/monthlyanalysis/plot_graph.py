import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def autolabel(rects):
	font = {'family': 'serif','color': 'black','weight': 'normal','size': 6.7}
	for rect in rects:
		height = rect.get_height()
		ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,'%0.1f' % float(height),ha='center', va='bottom',fontdict=font)

# f=open('isa_architect.txt','r')
# lines=f.readlines()

output_file_base_loc = '/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/year_analysis/year_2017_analysis.csv'
# output_file_base_loc = '/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/year_analysis/year_2016_analysis.csv'
# output_file_base_loc='/home/stealth/Sentiment/Sentimental_Work/ITC/Deleiverable-01/Twitter/Output_CSV_HARVARD/year_2017_analysis.csv'

d = pd.read_csv(output_file_base_loc)

month = list(d['Month'])
pos_score = list(d['Positive Percentage'])
neg_score = list(d['Negative Percentage'])
neutral_score = list(d['Neutral Percentage'])

# for line in lines:
# 	line=line.strip('\n')
# 	method.append(line.split()[0])
# 	score1.append(line.split()[1])
# 	score2.append(line.split()[2])

N = len(month)
ind = np.arange(N)
width = 0.25       # the width of the bars
fig, ax = plt.subplots()

rects1 = ax.bar(ind, pos_score, width, color='r')
rects2 = ax.bar(ind + width, neg_score, width, color='y')
rects3 = ax.bar(ind + width+width, neutral_score, width, color='b')

# add some text for labels, title and axes ticks
ax.set_ylabel('Percentage of Tweets (%)')
# ax.set_title('Year 2016 Sentiment Analysis Month wise')
ax.set_title('Year 2017 Sentiment Analysis Month wise')
ax.set_xticks(ind +width/2)
ax.set_xticklabels(month)

# plt.legend(loc=1)
params = {'legend.fontsize': 5.4}
plt.rcParams.update(params)
ax.legend((rects1[0], rects2[0], rects3[0]), ('Positive', 'Negative','Neutral'))

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

# plt.show()
# plt.savefig('/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/year_analysis/graph_2016_month_analysis.png')
plt.savefig('/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/year_analysis/graph_2017_month_analysis.png')

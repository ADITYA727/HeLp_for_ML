import numpy as np
import matplotlib.pyplot as plt

def autolabel(rects):
	font = {'family': 'serif','color': 'black','weight': 'normal','size': 7.3}
	for rect in rects:
		height = rect.get_height()
		ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,'%0.1f' % float(height),ha='center', va='bottom',fontdict=font)

N = 3
ind = np.arange(N)
width = 0.30       # the width of the bars
fig, ax = plt.subplots()

# No of tweets is: 40683
# Percentage of Positive Tweets is: 17.6707715754%
# Percentage of Negative Tweets is: 2.30808937394%
# Percentage of Neutral Tweets is: 80.0211390507%	

score1=['10.82','0.91','88.25']
rects1 = ax.bar(ind, score1, width, color='r')
ax.set_ylabel('Percentage of Tweets (%)')
ax.set_xticks(ind + width / 2)
ax.set_title('Total Tweets - 9714')
method=['Positive','Negative','Neutral']
ax.set_xticklabels(method)

# ax.legend((rects1[0]))

autolabel(rects1)
# autolabel(rects2)

# plt.show()
plt.savefig('/home/stealth/Sentiment/Sentimental_Work/Odisha/Twitter/output_csv/sentiment_stats_odisha_bjd.png')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import MySQLdb
import nltk
import sys
from nltk import word_tokenize as wordtoken
from nltk.probability import FreqDist as fredis
stopwords = nltk.corpus.stopwords.words('english')
import joblib
from unidecode import unidecode
from preprocessing import clean_tweet
import time
import itertools
from collections import Counter
import scipy as sp
from scipy import stats

db = MySQLdb.connect("52.172.205.54","ankur","ankur123","Twitter" )
cursor = db.cursor()

cities_list = joblib.load('/home/analytics/analytics/data/cities.txt')
states_list = joblib.load('/home/analytics/analytics/data/states.txt')

def double_quote(word):
    return '"{}"'.format(word)

cities_query = ' '.join([double_quote(city.lower()) for city in cities_list])
states_query = ' '.join([double_quote(state.lower()) for state in states_list])
combined_query = double_quote('india') + ' ' + cities_query + ' ' + states_query
cleaned_query = ' '.join([data for data in combined_query.split('(')])
final_query = cleaned_query.replace(')', '')
start_time = time.time()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import MySQLdb
import numpy as np
from collections import Counter

db = MySQLdb.connect("52.172.205.54","ankur","ankur123","Twitter" )
cursor = db.cursor()

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)

def plot_graphs(jaccard_values):
    d_arr = Counter(jaccard_values)
    d_arr = np.array(d_arr.items())
    d_arr = d_arr[d_arr[:,0].argsort()]
    d_arr = [list(d_arr[:,0]), list(d_arr[:,1].cumsum())]
    d_arr[1] = np.array(d_arr[1]) * 1.0 / np.array(d_arr[1]).max()

    plt.plot(d_arr[0], d_arr[1])
    plt.tick_params(axis='both', which='major')
    plt.xscale('log') 
    plt.xlabel('Jaccard values')
    plt.ylabel('CDF')
    plt.grid()
    plt.savefig('/home/analytics/analytics/sg_scripts/indian_users_jaccard.png')
    plt.clf()

def find_jaccard_score(user_tokens_dict):
    """ finds jaccard similarity between two Indian users

    :param: Dictionary with all Indian users
    :return: returns the value for jaccard coefficient
    """
    jaccard_values = []
    for (i,j) in itertools.combinations(user_tokens_dict,2):
        if len(set(user_tokens_dict[i]).union(set(user_tokens_dict[j]))) != 0:
            jaccard_value = round(len(set(user_tokens_dict[i]).intersection(set(user_tokens_dict[j]))) / len(set(user_tokens_dict[i]).union(set(user_tokens_dict[j]))), 2)
            jaccard_values.append(float(jaccard_value))
            with open('jaccard_values_indian_users.txt', 'a') as f:
                print(i, j, jaccard_value)
                f.write(i + ',')
                f.write(j + ',')
                f.write(str(jaccard_value) + '\n')
            f.close()
    
    plot_graphs(jaccard_values)
    print("--- Total time taken by program is %s seconds ---" % (time.time() - start_time))

def find_unigrams(complete_text, array_to_return):
    """ find unigrams for Indian users

    :param: Aggegrated tweet text of an Indian user, array where the tokens need to be returned
    :return: unigrams for that user ID
    """

    complete_text= str(complete_text).lower()
    tokens = clean_tweet(complete_text, stem=False, lemmatize=False, as_string=False)
    for token in tokens:
        if token not in array_to_return:
            array_to_return.append(token)
    
    return array_to_return

if __name__ == "__main__":
    user_tokens_dict = dict()
    user_query = """SELECT queue.user_handle FROM
                      queue JOIN user
                      ON queue.user_handle = user.user_handle
                      WHERE queue.tweet_status = 1 AND user.lang='en' AND user.total_tweet_count > 25 AND queue.query_id = 1 AND
                      MATCH (user.location, user.time_zone, user.description) AGAINST ('{}' IN BOOLEAN MODE);""".format(final_query)

    cursor.execute(user_query)
    results = cursor.fetchall()[:10]
    counter = 0
    total = len(results)

    for row in results:
        final_tokens = []
        counter = counter + 1
        print("Processing %s / %s" % (counter, total))
        user_complete_text = ''
        cursor.execute("SELECT text FROM Twitter.tweet WHERE user_handle=" + "'" + str(row[0]) + "'")
        user_tweet_results = cursor.fetchall()
        if len(user_tweet_results) > 0:            
            for each_result in user_tweet_results:
                if each_result[0] != '':
                    user_complete_text = str(user_complete_text) + unidecode(each_result[0])

            final_tokens_ = find_unigrams(user_complete_text, final_tokens)
            user_tokens_dict[row[0]] = final_tokens

    find_jaccard_score(user_tokens_dict)


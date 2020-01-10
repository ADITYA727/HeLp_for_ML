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

def find_jaccard_score(user_set1, user_set2, username):
    """ finds jaccard similarity between Indian and non Indian user

    :param: Indian and non-Indian user sets
    :return: returns the value for jaccard coefficient
    """

    jaccard_value = len(set(user_set1).intersection(set(user_set2))) / len(set(user_set2))
    print(jaccard_value)
    with open('jaccard_values.txt', 'a') as f:
        f.write(str(username) + "," + str(round(jaccard_value, 4)) + "\n")

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

def find_other_users_token(final_tokens_array):
    """ find tokens for non-Indian users
    
    :param: top30 tokens for all Indian users
    :return: calls another function to find jaccard similarity between sets
    """
    user_query = """SELECT queue.user_handle FROM
                      queue JOIN user
                      ON queue.user_handle = user.user_handle
                      WHERE queue.tweet_status = 1 AND user.lang='en' AND user.total_tweet_count > 25 AND queue.query_id = 1 AND
                      NOT MATCH (user.location, user.time_zone, user.description) AGAINST ('{}' IN BOOLEAN MODE);""".format(final_query)
    
    cursor.execute(user_query)
    results = cursor.fetchall()

    for row in results:
        final_tokens_array_nonIndian = []
        user_complete_text = ''
        cursor.execute("SELECT text FROM Twitter.tweet WHERE user_handle=" + "'" + str(row[0]) + "'")
        user_tweet_results = cursor.fetchall()
        if len(user_tweet_results) > 0:            
            for each_result in user_tweet_results:
                if each_result[0] != '':
                    user_complete_text = str(user_complete_text) + unidecode(each_result[0])

            final_tokens_array_nonIndian = find_unigrams(user_complete_text, final_tokens_array_nonIndian) 
            find_jaccard_score(final_tokens_array, final_tokens_array_nonIndian, row[0])
        else:
            print("Tweets not obtained for this user --", row[0])

    print("Time taken by the program to run", (time.clock() - start))

def prepare_data(results):
    """ find top 30 unigrams for all Indian users

    :params: All Indian users
    :return: calls another function to find overlap with other non-Indian user
    """

    total = len(results)
    counter = 0
    final_tokens_array = []

    for row in results:  
        user_complete_text = ''
        counter = counter + 1
        print("Processing %s / %s" % (counter, total))

        cursor.execute("SELECT text FROM Twitter.tweet WHERE user_handle=" + "'" + str(row[0]) + "'")
        user_tweet_results = cursor.fetchall()
        
        for each_result in user_tweet_results:
            if each_result[0] != '':
                user_complete_text = str(user_complete_text) + unidecode(each_result[0])

        final_tokens_array = find_unigrams(user_complete_text, final_tokens_array)

    print("Final tokens array length: ", len(final_tokens_array))
    print("Beginning analysis on non-Indian users")
    find_other_users_token(final_tokens_array)

if __name__ == "__main__":
    start = time.clock()
    print("Script started at:", start)
    user_query = """SELECT queue.user_handle FROM
                      queue JOIN user
                      ON queue.user_handle = user.user_handle
                      WHERE queue.tweet_status = 1 AND user.lang='en' AND user.total_tweet_count > 25 AND queue.query_id = 1 AND
                      MATCH (user.location, user.time_zone, user.description) AGAINST ('{}' IN BOOLEAN MODE);""".format(final_query)

    cursor.execute(user_query)
    results = cursor.fetchall()
    prepare_data(results)
   
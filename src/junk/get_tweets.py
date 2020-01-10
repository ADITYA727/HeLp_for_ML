import tweepy
import configparser
import pandas


class Tweets():
    def __init__(self):
        self.tweepy_api = None
        self.api = None

    def get_api(self):
        # Read the credentials from 'twitter-app-credentials.txt' file
        config = configparser.ConfigParser()
        config.read('/home/shubhamjain/Desktop/devel/stealth/src/twitter-credentials.txt')
        consumer_key = config['DEFAULT']['consumerKey']
        consumer_secret = config['DEFAULT']['consumerSecret']
        access_key = config['DEFAULT']['accessToken']
        access_secret = config['DEFAULT']['accessTokenSecret']

        # Create Auth object
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_key, access_secret)
        self.api = tweepy.API(auth)

        # Create stream and bind the listener to it
        self.tweepy_api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(),
                                     wait_on_rate_limit=True, wait_on_rate_limit_notify=True)



"""
python Exporter.py --querysearch "time magazine" --since 2015-08-03 --until 2015-09-03 --near '5,85'  --within '1500mi' --maxtweets 100000
"""
import pandas

path = '/home/shubhamjain/Desktop/devel/stealth/lib/GetOldTweets-python/'
df = pandas.read_csv(path+'time_magazine.csv',low_memory=False,error_bad_lines=False,sep=';')

tw = Tweets()
tw.get_api()

names = list(set(df['username']))

profiles = []
for name in names:
    profiles.append(tw.tweepy_api.lookup_users(screen_names=name))


import simplejson
f = open('/home/shubhamjain/Desktop/devel/stealth/lib/profiles.txt', 'w')
simplejson.dump(profiles, f)
f.close()


f = open('/home/shubhamjain/Desktop/devel/stealth/lib/profiles.txt', 'r')

tdf = pandas.read_csv('/home/shubhamjain/Desktop/devel/stealth/lib/GetOldTweets-python/odisha_election.csv', low_memory=False,error_bad_lines=False,sep=';')

full_text = ' '.join([str(item) for item in tdf['text']])
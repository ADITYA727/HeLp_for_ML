import time
import joblib
import grequests
import json
from bs4 import BeautifulSoup as BSoup
from dateutil import parser
import os
from datetime import datetime

from src.mysql_utils import MySqlUtils
from src.scraping.selenium_utils import SeleniumUtils
from selenium.common.exceptions import StaleElementReferenceException


home=os.path.abspath(os.path.dirname(__file__))


BASE_URL = 'https://www.twitter.com/'
URL_BATCH_SIZE = 200
GREQUESTS_SIZE = 100

USER_NAME = 'ramitsingh007'
PASSWORD='ramit@#$%'

class TwitterScraper:

    def __init__(self, headless=True):
        selenium_utils = SeleniumUtils(headless=headless)
        self.driver = selenium_utils.chrome_driver()

    # for twitter mobile website (because less content is loaded each time for scrolling)
    def login_to_twitter(self):
        """ Specify password and username and login to twitter
        :return: driver
        """
        print("Logging in...")
        self.driver.get("http://mobile.twitter.com/login")
        self.driver.implicitly_wait(4)
        username = self.driver.find_element_by_xpath(
            "//input[@name='session[username_or_email]' and @class='_1hXXD236 _1YGC8xFq ktZMpANQ _1VqMahaT _2Z8UymHS']")
        password = self.driver.find_element_by_xpath(
            "//input[@name='session[password]' and @class='_2Vbll_6C _1YGC8xFq ktZMpANQ _1VqMahaT _2Z8UymHS']")
        username.send_keys(USER_NAME)
        password.send_keys(PASSWORD)
        self.driver.find_element_by_xpath("//*[@id='react-root']/div/main/div/div/form/div/div[3]").click()
        print("Login Successful!")
        return self.driver

    def scrap_followers(self):
        """ Scrolls and fetches followers
        dumps every 1000 so that we have some data when we kill prematurely
        :return:
        """
        usernames = []  # list to append all username
        height = -1
        updated = 50
        count = 0

        # while loop ends when height remains same for 50 times
        while updated > 0:
            # newHeight = driver.execute_script("return document.body.scrollHeight")
            count = count + 1
            t1 = time.time()
            # take the html content each time when page is scrolled
            bs_obj = BSoup(self.driver.page_source, 'html.parser')
            try:
                #rows = bs_obj.find_all('b', {"class": "u-linkComplex-target"})
                rows = bs_obj.find_all('div',{"dir":"ltr"})

                for username in rows:
                    name=(username.text) #.split('@')[1]
                    #print("name original = ",name)
                    usernames.append(name)
                    #usernames.append('@'+name.lower().strip('?'))
                # to check the height
                height_new = self.driver.execute_script("return document.body.scrollHeight")
                if height == height_new:
                    updated = updated - 1
                else:
                    updated = 50
                height = height_new
            except StaleElementReferenceException:
                print("Exception")
                continue
            # page scrolling
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if count % 2 == 0:
                # checking how much time the program is taking
                print((time.time() - t1))
            if count % 1==0:
                print ("yielding")
                yield usernames
                usernames = []
                print("--------update userhandle in database for each 100 iteratoin ---------")


    def run_scrape_followers(self):
        # login in mobile twitter
        self.login_to_twitter()

        # get the followers
        self.driver.get('https://mobile.twitter.com/TIME/followers')
        self.scrap_followers()

    @staticmethod
    def yield_profile_requests(twitter_handles):
        """

        :param twitter_handles: includes @
        :return:
        """
        reqs = []
        for count, name in enumerate(twitter_handles):
            url = BASE_URL + name

            reqs.append(grequests.get(url, timeout=5))  # , session=sessions[i % NUM_SESSIONS]))
            if count % URL_BATCH_SIZE == 0 or count + 1 == len(twitter_handles):
                yield grequests.map(reqs, size=GREQUESTS_SIZE)
                reqs = []

    @staticmethod
    def get_profile_dictionary(response):
        res = BSoup(response.text)
        # scrap info from the twitter without using any api and login
        # get the json from the twitter html
        json_class = res.find_all('input', {'class': 'json-data'})
        json_data = json.loads(json_class[0].get('value'))
        data = {}
        # get all the information of the user
        if json_data.get('profile_user'):
            data['user_id'] = int(json_data['profile_user']['id'])
            data['user_handle'] = str('@'+json_data['profile_user']['screen_name']).lower().encode('utf-8')
            if json_data['profile_user']['created_at']:
                data['created_at'] = parser.parse(json_data['profile_user']['created_at'])
            data['description'] = str(json_data['profile_user']['description']).encode()
            data['description_url'] = str(json_data['profile_user']['url']).encode()[:99]
            data['location'] = json_data['profile_user']['location'].encode()[:99]
            data['followers_count'] = json_data['profile_user']['followers_count']
            data['likes_count'] = json_data['profile_user']['favourites_count']
            data['following_count'] = json_data['profile_user']['friends_count']
            data['actual_name'] = json_data['profile_user']['name'].encode()[:99]
            data['profile_image_url'] = json_data['profile_user']['profile_image_url']
            data['total_tweet_count'] = json_data['profile_user']['statuses_count']
            data['time_zone'] = json_data['profile_user']['time_zone']
            data['protected'] = json_data['profile_user']['protected']
            data['verified'] = json_data['profile_user']['verified']
            data['lang'] = json_data['profile_user']['lang']
            data['geo_enabled'] = json_data['profile_user']['geo_enabled']
            data['utc_offset'] = json_data['profile_user']['utc_offset']
            #data['last_updated']=datetime.now()
        return data

    def run_store_profile_info(self,names,query_id):
        sql = MySqlUtils()
        non_processed_handles = names   # list
        responses_iterator = self.yield_profile_requests(non_processed_handles)
        for responses in responses_iterator:
            for response in responses:
                if response and response.status_code == 200:
                    twitter_user_dictionary = self.get_profile_dictionary(response,query_id)
                    try:
                        sql.dict_to_sql(twitter_user_dictionary, 'user')
                    except Exception as e:
                        print(e)
                        print(twitter_user_dictionary)

    def close(self):
        """

        :return:
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

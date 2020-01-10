from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from bs4 import BeautifulSoup as BS
import joblib
import time
import os
import sys
import time
from collections import deque



username = ['ganapatel@outlook.com']
password = ['gana@#$%']




GROUP_MEMBERS = 32000  # Scrape this from page at some point
PROXY = "socks5://127.0.0.1:9050"


class ScrapeFacebookSangli:

    def __init__(self, headless=False, scroll_iterations=10, use_tor=False):
        self.cursor = None
        self.names = None
        self.designations = None
        self.scraped_count = 0
        self.headless = headless
        self.use_tor = use_tor
        self.driver = self.chrome_driver()
        self.scroll_iterations = scroll_iterations
        self.flag=0
        self.count=0


    def chrome_driver(self):
        """ Get browser driver for chrome. Chrome Options to remove notifications
        :return: driver
        """
        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")
        if self.use_tor:
            chrome_options.add_argument('--proxy-server=%s' % PROXY)
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(chrome_options=chrome_options,
                                executable_path='../../lib/chromedriver')


    def close(self):
        """

        :return:
        """
        if self.driver:
            self.driver.close()
            self.driver = None
        self.cur.close()
        self.db.close()

    def login_to_facebook(self,username,password):
        """ Specify password and username and login to facebook

        :return: driver
        """
        print("Logging in...")
        self.driver.get("https://www.facebook.com/")
        self.driver.find_element_by_id("email").send_keys(username)
        self.driver.find_element_by_id("pass").send_keys(password)
        self.driver.find_element_by_id("loginbutton").click()
        print("Login Successful!")

    def scroll(self):
        """

        :return:
        """

        for i in range(self.scroll_iterations):
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scrape_desired_group_elements(self):
        """ Connect to facebook group and identify names and designations elements

        :return: names and designations elements
        """

        # find name and designation elements
        # self.designations = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_class_name("clearfix""))
        # self.names = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_class_name("_60ri"))
        self.login_to_facebook()
        self.driver.get('https://www.facebook.com/search/str/sangli/pages-named/residents/present/intersect/')
        self.scroll()
        try:
            urls1 = joblib.load('fb_links.txt')
        except Exception as e:
            print(e)
            urls1 = list()
        soup = BS(self.driver.page_source, 'html.parser')

        # print(soup.contents)
        clas = soup.find_all('div', {'class': "clearfix"})
        link_url = []
        count = 0
        for link in clas:
            count = count + 1
            urls = link.find_all("a", {'class': '_ohe'})
            for url in urls:
                user_url = url.attrs["href"] if "href" in url.attrs else ''
                link_url.append(user_url)
                print("URL: {} Count: {}".format(link_url, count))
        urls1.extend(link_url)
        joblib.dump(urls1, 'fb_links.txt')

        """
        for anchor in clas.find_all("a",{'class':'_ohe'}):

            # extract link url from the anchor
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''
            link_url.append(link)
            print(link)
        joblib.dump(link_url,'fb_links.txt')
        """

    def scrape_posts(self):
        self.login_to_facebook(username[self.flag],password[self.flag])
        try:
            posts = joblib.load('fb_posts1.txt')
        except Exception as e:
            print("links",e)
            posts = list()
        try :
            unprocessed_url=joblib.load('unprocessed_fb_urls.txt')
        except Exception as e:
            print("unprocessed_url ",e)
            links = joblib.load('fb_links.txt')
            links = list(set(links))
            unprocessed_url=deque(links)
        try:
            processed_url = joblib.load('processed_fb_urls.txt')
        except Exception as e:
            print("processed_url ", e)
            processed_url = list()

        while unprocessed_url:
            link = unprocessed_url.popleft()
            self.count = self.count+1
            self.driver.get(link)
            self.scroll()
            soup = BS(self.driver.page_source, 'html.parser')
            posts_data=[]
            check_fb_permission = soup.find('div',{'class':'uiInterstitial'})
            if check_fb_permission:
                # logout
                self.driver.find_element_by_xpath("//div[@id='userNavigationLabel']").click();
                time.sleep(1)
                self.driver.find_element_by_xpath('//form[@class="_w0d _w0d"]').submit();
                self.flag=self.flag+1
                # check
                unprocessed_url.append(link)
                joblib.dump(posts,'fb_posts1.txt')
                joblib.dump(posts,'unprocessed_fb_urls.txt')
                joblib.dump(posts,'processed_fb_urls.txt')
                self.scrape_posts()

            clas = soup.find_all('div', {'class': "userContent"})
            for data in clas:
                if data:
                    text = data.getText()
                    posts_data.append(text)
            posts.extend(posts_data)

            processed_url.append(link)

            print(" facebook profile url ==> ", link)
            print (" no. of posts ==> ", len(posts_data))
            print("processed_urls ==> ", len(processed_url))
            print("unprocessed_urls ==> ", len(unprocessed_url))

            if self.count%100==0:
                print("------- got {} users posts ------".format(self.count))
                joblib.dump(posts,'fb_posts1.txt')
                joblib.dump(posts,'unprocessed_fb_urls.txt')
                joblib.dump(posts,'processed_fb_urls.txt')
            time.sleep(15)

        print("------- got {} users posts ------".format(self.count))
        joblib.dump(posts,'fb_posts1.txt')
        joblib.dump(posts,'unprocessed_fb_urls.txt')
        joblib.dump(posts,'processed_fb_urls.txt')

    def run(self):
        """
        :return:
        """
        #self.scrape_desired_group_elements()
        self.scrape_posts()



a = ScrapeFacebookSangli()
a.run()

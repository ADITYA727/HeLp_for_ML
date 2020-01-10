import string
import threading
from collections import defaultdict

import MySQLdb
from MySQLdb import IntegrityError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import os, sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from src.scraping.scraping_utils import get_last_name, get_first_name  # noinspection

username = 'virtuositscraping_utilsy01@gmail.com'
password = ''
GROUP_MEMBERS = 32000  # Scrape this from page at some point
PROXY = "socks5://127.0.0.1:9050"  # IP:PORT or HOST:PORT # tor

"""
Steps
1. Install Tor Server
2. Install Mysql server
3. Install python packages
4. Setup database
5. run_thread()

Install
TODO: Incorrect string value, ascii issue
TODO: Bulk insert
TODO: Add DB to init of class.
TODO: multiple matches in directory
TODO: first name in 3 word names

service tor start

SHOW DATABASES;
CREATE DATABASE Members;
Select * from Members;
mysql -u root Members < dump1.sql

CREATE TABLE Members (
   Screen_name VARCHAR(1000) NOT NULL,
   Description VARCHAR(1000) NOT NULL,
   Fb_url VARCHAR(100) NOT NULL UNIQUE TRUE,
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

ALTER TABLE Members ADD UNIQUE KEY 'email';

mysql -u root
use Members;
ALTER TABLE Members
  ADD COLUMN name_hw VARCHAR(1000),
  ADD COLUMN department VARCHAR(1000),
  ADD COLUMN appointment_title VARCHAR(1000),
  ADD COLUMN university_mailing_address VARCHAR(1000),
  ADD COLUMN email VARCHAR(1000),
  ADD COLUMN residence VARCHAR(1000),
  ADD COLUMN home_phone VARCHAR(1000),
  ADD COLUMN office_phone VARCHAR(1000),
  ADD COLUMN unit VARCHAR(1000);
  ADD column harvard_url VARCHAR(1000);

ALTER TABLE Members MODIFY COLUMN Screen_name VARCHAR(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

"""


class ScrapeFacebookGroups:
    """ Scrape Facebook Groups

    """

    def __init__(self, headless=True, scroll_iterations=GROUP_MEMBERS * 10, use_tor=False):
        self.cursor = None
        self.names = None
        self.designations = None
        self.scraped_count = 0
        self.headless = headless
        self.use_tor = use_tor
        self.driver = self.chrome_driver()
        self.scroll_iterations = scroll_iterations
        self.db = MySQLdb.connect(host="localhost", user="root", db="Members")
        self.db.set_character_set('utf8mb4')
        self.cur = self.db.cursor()

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

    @staticmethod
    def firefox_driver():
        """ Get driver for firefox
        :return: driver
        """
        binary = FirefoxBinary("/home/sachin/firefox/firefox-bin")
        return webdriver.Firefox(firefox_binary=binary)

    def close(self):
        """

        :return:
        """
        if self.driver:
            self.driver.close()
            self.driver = None
        self.cur.close()
        self.db.close()

    def login_to_facebook(self):
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
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scrape_desired_group_elements(self):
        """ Connect to facebook group and identify names and designations elements

        :return: names and designations elements
        """

        # find name and designation elements
        # self.designations = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_class_name("_60rj"))
        # self.names = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_class_name("_60ri"))
        self.designations = self.driver.find_elements_by_class_name("_60rj")
        self.names = self.driver.find_elements_by_class_name("_60ri")

    def write_to_database(self):
        """
        :return:
        """

        print("Writing {} records of {} to database".format(len(self.designations) - self.scraped_count,
                                                            self.scraped_count))
        for counter, (designation, name) in enumerate(zip(self.designations, self.names)):
            # After every scroll all the elements are scraped from top of the page.
            if counter < self.scraped_count:
                continue

            self.scraped_count += 1
            q = """INSERT INTO Members (Screen_name, Description, Fb_url) VALUES (%s, %s, %s)"""
            try:
                name_text = str(name.text)
                designation = str(designation.text)
                url = str(name.find_element_by_css_selector('._60ri a').get_attribute('href'))

                self.cursor.execute(q, (name_text, designation, url))
                self.db.commit()
            except Exception as e:
                print(str(e.args) + " " + str(e))

    def run(self):
        """

        :return:
        """
        self.login_to_facebook()
        self.driver.get('https://www.facebook.com/groups/groupsatharvard/members/')
        self.scroll()
        self.scrape_desired_group_elements()
        self.write_to_database()
        self.close()


class ScrapeHarvardDirectory:
    """ Scrape Harvard Directory

    """

    def __init__(self, headless=True, use_tor=True):
        self.driver = ScrapeFacebookGroups(headless=headless, use_tor=use_tor).chrome_driver()
        self.db = MySQLdb.connect(host="localhost", user="root", db="Members")
        self.db.set_character_set('utf8mb4')
        self.write_cursor = self.db.cursor()
        self.read_cursor = self.db.cursor()
        self.retry = 0
        self.url = 'https://www.directory.harvard.edu/phonebook/'
        self.content_page_url = "https://www.directory.harvard.edu/phonebook/submitSearch.do"
        self.first_name = ''
        self.last_name = ''

    def scrape_harvard_website(self):
        """ The main scraping function.
        Passes first name and last name arguments and click to the content page.
        """
        # load the harvard directory home page, enter the firstname and last name and press submit
        try:
            self.driver.get(self.url)
            # print('Home Page Loaded')
            element = self.driver.find_element_by_xpath(
                """//*[@id="welcome"]/table/tbody/tr/td/table/tbody/tr/td[3]/form/table/tbody/tr[2]/td[2]/font/input""")
            element.clear()
            element.send_keys(self.last_name)
            element = self.driver.find_element_by_xpath(
                """//*[@id="welcome"]/table/tbody/tr/td/table/tbody/tr/td[3]/form/table/tbody/tr[3]/td[2]/font/input""")
            element.clear()
            element.send_keys(self.first_name)
            element = self.driver.find_element_by_xpath("""//*[@id="search"]""")
            element.click()
            # print("Clicked Submit")
        except NoSuchElementException as e:
            # No Internet?
            print("Error {} \nRetrying...{}".format(e, self.retry))
            self.retry += 1
            if self.retry < 5:
                self.scrape_harvard_website()
            raise SystemExit
        except TimeoutException as e:
            # Slow Internet?
            print("Error {} \nRetrying...{}".format(e, self.retry))
            self.retry += 1
            if self.retry < 5:
                self.scrape_harvard_website()
            raise SystemExit

        self.extract_content()

    def extract_content(self):
        """

        :return:
        """
        # page has not redirected to content page
        # print("extract content")
        try:
            # print('first try')
            # No items found text on home page
            element = self.driver.find_element_by_xpath(
                """//*[@id="welcome"]/table/tbody/tr/td/table/tbody/tr/td[3]/form/table/tbody/tr[1]/td/b/p/font""")
            # print(element.text)
        except NoSuchElementException:
            try:
                # print('second try')
                content = self.driver.find_element_by_xpath(
                    """//*[@id="welcome"]/table/tbody/tr/td/center/table/tbody/tr[1]/td[2]/form/table/tbody""")
                print(content.text)
                return content.text
            except NoSuchElementException:
                # Slow Internet/some other error
                try:
                    # print('third try')
                    content = self.driver.find_element_by_xpath(
                        """//*[@id="welcome"]/table/tbody/tr/td/center/table/tbody/tr[1]/td[2]/table/tbody[2]""")
                    generic_xpath = '//*[@id="welcome"]/table/tbody/tr/td/center/table/tbody/tr[1]/td[2]/table/tbody[2]/tr[{}]/td[1]/font/a'
                    table = content.find_element_by_xpath(
                        '//*[@id="welcome"]/table/tbody/tr/td/center/table/tbody/tr[1]/td[2]/table/tbody[2]')
                    url_list = []
                    for i in range(1, table.text.count('\n') + 1):
                        xpath = generic_xpath.format(i)
                        person = content.find_element_by_xpath(xpath)
                        url_list.append(person.get_attribute('href'))
                    for url in url_list:
                        self.driver.get(url)
                        text = self.extract_content()
                        # print('content received')
                        print(text)
                        record = self.text_to_columns(text)
                        self.write_to_database(record)
                        # print('database updated')
                        print(record)
                except NoSuchElementException as e:
                    self.retry += 1
                    if self.retry < 5:
                        print("Error {} \nRetrying...{}".format(e, self.retry))
                        self.scrape_harvard_website()

    @staticmethod
    def text_to_columns(text):
        """
        :return:
        """
        record = defaultdict()
        try:
            text_list = text.split('\n')
            for item in text_list:
                if item.split(':') and item.split(':')[0] == 'Email':
                    record['email'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Name':
                    record['name_hw'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Department':
                    record['department'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Appointment Title':
                    record['appointment_title'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'University Mailing Address':
                    record['university_mailing_address'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Residence':
                    record['residence'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Home Phone':
                    record['home_phone'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Office Phone':
                    record['office_phone'] = item.split(':')[1]
                if item.split(':') and item.split(':')[0] == 'Unit':
                    record['unit'] = item.split(':')[1]
                elif record.get('university_mailing_address') and ':' not in item:
                    record['university_mailing_address'] = "{}\n{}".format(record.get('university_mailing_address'),
                                                                           item)
                elif record.get('residence') and ':' not in item:
                    record['residence'] = "{}\n{}".format(record.get('residence'), item)
        except:
            print(text)
        return record

    def update_database(self, record, row=None):
        """

        :param record:
        :param row:
        :return:
        """
        if row is None:
            row = {}
        q2 = """UPDATE Members
                SET
                    name_hw = %s,
                    department = %s,
                    appointment_title = %s,
                    university_mailing_address = %s,
                    email = %s,
                    residence = %s,
                    home_phone = %s,
                    office_phone = %s,
                    unit = %s
                WHERE
                    S_no = %s"""
        self.write_cursor.execute(q2, (
            record.get('name_hw'), record.get('department'),
            record.get('appointment_title'),
            record.get('university_mailing_address'), record.get('email'), record.get('residence'),
            record.get('home_phone'), record.get('office_phone'), record.get('unit'), row[0]))
        self.db.commit()
        print(record)

    def write_to_database(self, record):
        """
        :return:
        """
        q2 = """
            INSERT
            INTO
            Members(
                name_hw,
                department,
                appointment_title,
                university_mailing_address,
                email,
                residence,
                home_phone,
                office_phone,
                unit
            )
            VALUES( % s, % s, % s, % s, % s, % s, % s, % s, % s)"""
        try:
            self.write_cursor.execute(q2, (
                record.get('name_hw'), record.get('department'),
                record.get('appointment_title'),
                record.get('university_mailing_address'), record.get('email'), record.get('residence'),
                record.get('home_phone'), record.get('office_phone'), record.get('unit')))
            self.db.commit()
        except IntegrityError:
            print('Integrity error')
        # print("added to database")
        # print(record)

    def run(self, thread_id):
        """
        :return:
        """
        q = """
        SELECT
        S_no, Screen_name, Description, Fb_url
        FROM
        Members
        """
        self.read_cursor.execute(q)
        row = self.read_cursor.fetchone()
        count = 0
        while row is not None:
            count += 1
            print("{} {} {}".format(row[0], count, thread_id))
            if (thread_id and count % 5 == thread_id and count > 0) or (not thread_id and count > 0):
                self.retry = 0
                content = self.scrape_harvard_website(get_first_name(row[1]), get_last_name(row[1]))
                if content:
                    record = self.text_to_columns(content)
                    self.update_database(record, row)
            row = self.read_cursor.fetchone()
        self.close()

    def run_from_text_file(self):
        """
        :return:
        """
        f = open("data/Board of Overseers.txt", "r")
        for count, line in enumerate(f):
            if count % 3 == 0:
                self.first_name = get_first_name(line.split('(')[0])
                self.last_name = get_last_name(line.split('(')[0])
                content = self.scrape_harvard_website()
                print(content)
                if content:
                    record = self.text_to_columns(content)
                    self.write_to_database(record)

    def run_brute_force(self, thread_id=None):
        """
        :return:
        """
        self.last_name = ''
        count = 0
        for letter1 in string.ascii_lowercase:
            for letter2 in string.ascii_lowercase:
                for letter3 in string.ascii_lowercase:
                    for letter4 in string.ascii_lowercase:
                        if (thread_id is not None and count % 5 == thread_id) or thread_id is None:
                            print(count)
                            self.first_name = "{}{}{}{}*".format(letter1, letter2, letter3, letter4)
                            print(self.first_name)
                            if count > 26000:
                                content = self.scrape_harvard_website()
                                print(content)
                                if content:
                                    record = self.text_to_columns(content)
                                    self.write_to_database(record)
                        count += 1
        self.close()

    def run_brute_force2(self, thread_id=None):
        """
        :return:
        """
        q = """
        SELECT
        S_no, Screen_name, Description, Fb_url
        FROM
        Members
        ORDER BY
        S_no
        """
        self.read_cursor.execute(q)
        row = self.read_cursor.fetchone()
        while row is not None:
            print(row[0])
            if (thread_id and row[0] % 5 == thread_id and row[0] > 250) or (not thread_id and row[0] > 250):
                self.retry = 0

                self.first_name = get_first_name(row[1])
                self.last_name = ''
                content = self.scrape_harvard_website()
                if content:
                    record = self.text_to_columns(content)
                    self.write_to_database(record)

                self.first_name = ''
                self.last_name = get_last_name(row[1])
                content = self.scrape_harvard_website()
                if content:
                    record = self.text_to_columns(content)
                    self.write_to_database(record)
            print(row[0])
            row = self.read_cursor.fetchone()
        self.close()

    def close(self):
        """

        :return:
        """
        if self.driver:
            self.driver.close()
            self.driver = None
            self.write_cursor.close()
            self.read_cursor.close()
            self.db.close()


def run_thread():
    """

    :return:
    """
    threads = []
    # s = ScrapeHarvardDirectory(use_tor=True, headless=False)
    # s.run_brute_force()
    for i in range(5):
        s = ScrapeHarvardDirectory(use_tor=True, headless=True)
        t = threading.Thread(target=s.run_brute_force, args=[i])
        threads.append(t)
        t.start()

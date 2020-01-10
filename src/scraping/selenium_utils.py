from selenium import webdriver
import os

PROXY = "socks5://127.0.0.1:9050"  # IP:PORT or HOST:PORT # tor
home=os.path.abspath(os.path.dirname(__file__))


class SeleniumUtils:
    def __init__(self, headless=True, use_tor=False):
        self.headless = headless
        self.use_tor = use_tor

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
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=home+'/../../lib/chromedriver')
        return driver

    @staticmethod
    def firefox_driver():
        """ Get driver for firefox
        :return: driver
        """
        driver = webdriver.Firefox(executable_path='../../lib/geckodriver')
        return driver

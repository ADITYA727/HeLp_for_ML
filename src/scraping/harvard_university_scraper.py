#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 14:45:08 2017

@author: stealth
"""

import re
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import grequests
import joblib
import time
import os, sys
from memory_profiler import profile

home = os.path.abspath(os.path.dirname(__file__))

URL_BATCH_SIZE = 100
GREQUESTS_SIZE = 100
TOTAL_TIMEOUT=20
regex = re.compile(r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+")
allowed_domain = ['hks', 'hls', 'hbs']


class UniversityScraper:

    def __init__(self):
        urls = ['https://www.hks.harvard.edu', 'http://hls.harvard.edu', 'https://www.hbs.edu/Pages/default.aspx']
        self.extentions = ['.pdf', '.ptx', '.jpg', '.m4a', '.mp3', '.doc', '.png', '.zip', '.ocx', '.ppt', '.pptx',
                           '.docx', '.xls', '.xlsx', 'jpeg']
        # self.data = pd.read_csv(home + '/../../data/url.csv')
        # for i in range(0, len(self.data)):
        #     if 'faculty' in self.data['url'][i]:
        #         urls.append(self.data['url'][i])
        self.count = 10

        # starting url. replace google with your own url.
        self.starting_url = urls
        # process urls one by one from unprocessed_url queue until queue is empty

        # set of already crawled urls for email
        try:
            self.processed_urls = joblib.load(home + '/../../data/processed_urls2.txt')
        except Exception as e:
            print(e)
            self.processed_urls = list()

        # a queue of urls to be crawled
        try:
            self.unprocessed_urls = joblib.load(home + '/../../data/unprocessed_urls2.txt')
        except Exception as e:
            print(e)
            self.unprocessed_urls = deque(self.starting_url)
        # a set of fetched emails
        try:
            self.emails = joblib.load(home + '/../../data/emails2.txt')
        except Exception as e:
            print(e)
            self.emails = list()

    def get_requests_and_urls_to_scrape(self):
        reqs = []
        base_url_list = []
        path_list = []
        for i in range(URL_BATCH_SIZE):
            if self.unprocessed_urls:
                url = self.unprocessed_urls.popleft()
                self.processed_urls.append(url)

                # extract base url to resolve relative links
                parts = urlsplit(url)
                base_url_list.append("{0.scheme}://{0.netloc}".format(parts))
                path_list.append(url[:url.rfind('/') + 1] if '/' in parts.path else url)
                # get url's content
                print("Crawling URL %s" % url)
                if all([i not in url for i in self.extentions]):
                    reqs.append(grequests.get(url, timeout=10, stream=False))  # , session=sessions[i % NUM_SESSIONS]))
        return reqs, base_url_list, path_list

    def get_email_from_page(self, response=None):

        new_emails = regex.findall(response.text, re.I)
        #print(response.url)
        self.emails.extend(new_emails)

        # print(response)
        # print(emails)
        # create a beutiful soup for the html document

        soup = BeautifulSoup(response.text, 'lxml')

        return soup

        # Once this document is parsed and processed, now find and process all the anchors i.e.
        # linked urls in this document

    def get_links_from_page(self, soup=None, base_url=None, path=None, processed_urls_hash=None):

        for anchor in soup.find_all("a"):

            # extract link url from the anchor
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''
            # resolve relative links (starting with /)
            if link and all([i not in link for i in self.extentions]):
                if link[0] == '/':
                    link = base_url + link
                elif not link[:4] == 'http':
                    link = path + link
                # add the new url to the queue if it was not in unprocessed list nor in processed list yet
                if any([i in link[:30] for i in
                        allowed_domain]) and not processed_urls_hash.get(link):
                    # domain harvard and hbs only
                    # dom = tldextract.extract(link).domain
                    # if dom in allowed_domain:
                    self.unprocessed_urls.append(link)


    def write_into_file(self):
        if self.count < 1:
            self.count = 10
            joblib.dump(self.processed_urls, home + '/../../data/processed_urls2.txt')
            joblib.dump(deque(set(self.unprocessed_urls)), home + '/../../data/unprocessed_urls2.txt')
            joblib.dump(list(set(self.emails)), home + '/../../data/emails2.txt')
    @profile
    def main(self):

        # move next url from the queue to the set of processed urls
        # tuple of args for foo

        self.count = self.count - 1
        print('Emails: {}'.format(len(self.emails)))
        print('Unprocessed URLs: {}'.format(len(self.unprocessed_urls)))
        print('Processed URLS: {}'.format(len(self.processed_urls)))
        t3 = time.time()

        reqs, base_url_list, path_list = self.get_requests_and_urls_to_scrape()
        print('Sending Grequests')
        response_list = grequests.map(reqs, size=GREQUESTS_SIZE, gtimeout=TOTAL_TIMEOUT)  # get the return value from your function.
        # extract all email addresses and add them into the resulting set
        # You may edit the regular expression as per your requirementt
        t4 = time.time()
        print("Request completed in {}".format(time.time() - t3))
        processed_urls_hash = dict.fromkeys(self.processed_urls)
        print(response_list)
        for response, base_url, path in zip(response_list, base_url_list, path_list):
            if response:
                soup = self.get_email_from_page(response=response)
                self.get_links_from_page(soup=soup, base_url=base_url, path=path,
                                         processed_urls_hash=processed_urls_hash)
                soup.decompose()

        t2 = time.time()
        print("Scraping complete in {}".format(t2 - t4))
        self.write_into_file()
        print("Writing completed in {}".format(time.time() - t2))


a=UniversityScraper()
while a.unprocessed_urls:
    a.main()

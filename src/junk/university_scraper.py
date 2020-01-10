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
import pandas as pd
import grequests
import joblib
import time
import os

home = os.path.abspath(os.path.dirname(__file__))

URL_BATCH_SIZE = 200
GREQUESTS_SIZE = 100
regex = re.compile(r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+")


def main():
    urls = []
    allowed_domain = ['harvard', 'hbs']
    data = pd.read_csv(home + '/../../data/url.csv')
    for i in range(0, len(data)):
        if 'faculty' in data['url'][i]:
            urls.append(data['url'][i])

    # starting url. replace google with your own url.
    starting_url = urls
    # process urls one by one from unprocessed_url queue until queue is empty

    # set of already crawled urls for email
    try:
        processed_urls = joblib.load(home + '/../../data/processed_urls.txt')
    except Exception as e:
        print(e)
        processed_urls = list()

    # a queue of urls to be crawled
    try:
        unprocessed_urls = joblib.load(home + '/../../data/unprocessed_urls1.txt')
    except Exception as e:
        print(e)
        unprocessed_urls = deque(starting_url)

    # a set of fetched emails
    try:
        emails = joblib.load(home + '/../../data/emails1.txt')
    except Exception as e:
        print(e)
        emails = list()
    count = 10
    while unprocessed_urls:

        # move next url from the queue to the set of processed urls
        # tuple of args for foo
        reqs = []
        base_url_list = []
        path_list = []
        count = count - 1
        for i in range(URL_BATCH_SIZE):
            if unprocessed_urls:
                url = unprocessed_urls.popleft()
                processed_urls.append(url)

                # extract base url to resolve relative links
                parts = urlsplit(url)
                base_url_list.append("{0.scheme}://{0.netloc}".format(parts))
                path_list.append(url[:url.rfind('/') + 1] if '/' in parts.path else url)

                # get url's content
                # print("Crawling URL %s" % url)
                extentions = ['.pdf', '.ptx', '.jpg', '.m4a', '.mp3', '.doc', '.png', '.zip', '.ocx', '.ppt', '.pptx',
                              '.docx', '.xls', '.xlsx', 'jpeg']
                if all([i not in url for i in extentions]):
                    reqs.append(grequests.get(url, timeout=2))  # , session=sessions[i % NUM_SESSIONS]))

        print('Emails: {}'.format(len(emails)))
        print('Unprocessed URLs: {}'.format(len(unprocessed_urls)))
        print('Processed URLS: {}'.format(len(processed_urls)))
        t3 = time.time()
        response_list = grequests.map(reqs, size=GREQUESTS_SIZE)  # get the return value from your function.
        # extract all email addresses and add them into the resulting set
        # You may edit the regular expression as per your requirementt
        t4 = time.time()
        print("Request completed in {}".format(time.time() - t3))
        processed_urls_hash = dict.fromkeys(processed_urls)
        for response, base_url, path in zip(response_list, base_url_list, path_list):
            if response:
                t0 = time.time()
                new_emails = regex.findall(response.text, re.I)
                if time.time() - t0 > 1:
                    print(response.url)
                emails.extend(new_emails)

                # print(response)
                # print(emails)
                # create a beutiful soup for the html document

                soup = BeautifulSoup(response.text, 'lxml')

                # Once this document is parsed and processed, now find and process all the anchors i.e.
                # linked urls in this document

                for anchor in soup.find_all("a"):

                    # extract link url from the anchor
                    link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                    # resolve relative links (starting with /)
                    if link:
                        if link[0] == '/':
                            link = base_url + link
                        elif not link[:4] == 'http':
                            link = path + link
                        # add the new url to the queue if it was not in unprocessed list nor in processed list yet
                        if any([i in link[:30] for i in
                                allowed_domain]) and processed_urls_hash.get(link):
                            # domain harvard and hbs only
                            # dom = tldextract.extract(link).domain
                            # if dom in allowed_domain:
                            unprocessed_urls.append(link)

        t2 = time.time()
        print("Scraping Time: {}".format(t2 - t4))
        if count < 1:
            count = 10
            joblib.dump(processed_urls, home + '/../../data/processed_urls.txt')
            joblib.dump(deque(set(unprocessed_urls)), home + '/../../data/unprocessed_urls1.txt')
            joblib.dump(list(set(emails)), home + '/../../data/emails1.txt')
            print("Writing completed in {}".format(time.time() - t2))


main()

"""
todo: instagram images are not searched by google search image because they are not accessible.
"""

import requests
import os, sys
home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.mysql_utils import MySqlUtils
from bs4 import BeautifulSoup as b

from urllib.parse import quote_plus as q, unquote_plus as unq, urlencode
from urllib.request import build_opener, urlopen, HTTPCookieProcessor, urlparse
from http.cookiejar import CookieJar
import re
import joblib


BASE_URL = 'https://www.google.co.jp'
BASE_SEARCH_URL = BASE_URL + '/searchbyimage?%s'

REFERER_KEY = 'Referer'
image_ext = ['.ani', '.bmp', '.cal', '.fax', '.gif', '.img', '.jbg', '.jpe', '.jpeg', '.jpg', '.mac', '.pbm', '.pcd',
             '.pcx', '.pct', '.pgm', '.png', '.ppm', '.psd', '.ras', '.tga', '.tiff', '.wmf']

Opener = build_opener(HTTPCookieProcessor(CookieJar()))
Opener.addheaders = [
    ('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'),
    ('Accept-Language', 'ja,en-us;q=0.7,en;q=0.3')
]

image_url_pattern = re.compile(r'^http://www.google.co.jp/imgres\?imgurl=(?P<url>[^&]+)')


def double_quote(word):
    # return f'"{word}"' # python 3.6 onwards
    return '"{}"'.format(word)


cities_list = joblib.load(home + '/../../data/cities.txt')
states_list = joblib.load(home + '/../../data/states.txt')

cities_query = ' '.join([double_quote(city.lower()) for city in cities_list])
states_query = ' '.join([double_quote(state.lower()) for state in states_list])
combined_query = double_quote('india') + ' ' + cities_query + ' ' + states_query
cleaned_query = ' '.join([data for data in combined_query.split('(')])
final_query = cleaned_query.replace(')', '')
print(final_query)
user_query = """SELECT queue.user_handle FROM
                  queue JOIN user
                  ON queue.user_handle = user.user_handle
                  WHERE
                  queue.tweet_status=1 AND user.lang='en' AND
                  user.total_tweet_count > 25 AND queue.query_id=1 AND
                      MATCH (user.location, user.time_zone, user.description) AGAINST ('{}' IN BOOLEAN MODE);""".format(final_query)


def get_referer_index():
    i = 0
    for k, v in Opener.addheaders:
        if k == REFERER_KEY:
            return i
        i += 1
    else:
        return None


def get_referer():
    cur = get_referer_index()
    if cur is not None:
        return Opener.addheaders[cur]
    else:
        return None


def set_referer(url):
    cur = get_referer_index()
    if cur is not None:
        del Opener.addheaders[cur]
    Opener.addheaders.append(
        (REFERER_KEY, url)
    )


def search_image(url):
    params = {
        'image_url': url,
        'hl': 'ja',
    }
    query = BASE_SEARCH_URL % urlencode(params)
    f = Opener.open(query)
    url = f.url
    # domain
    # url += '&as_sitesearch=zozo.jp'
    f = Opener.open(url)
    html = f.read()
    set_referer(f.url)
    return html


def get_content_from_images(html):
    content = ''
    soup = b(html)
    text_class = soup.find_all('div', {'class': 'rc'})
    for text in text_class:
        content = content + text.text
    return content


def get_content_from_urls(html):
    soup = b(html)
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def get_content(url):
    content = ''
    url_split = url['urls_contained'].split(',')
    print(url_split)
    for u in url_split:
        print(u)
        # for error 404
        # checking image url
        try:
            response = requests.get(u,timeout=1)
        except Exception as e:
            print("Exception in requesting url", e)
            continue
        if response and not'pdf' in response.url:
            url_check = [u.endswith(ext) for ext in image_ext]
            if any(url_check):
                print("--------------------google search image-------------------------")
                try:
                    html = search_image(u)
                except Exception as e:
                    print("Exception in search image ", e)
                # getting content from google search image
                text = get_content_from_images(html)

            elif 'https://twitter.com' in u:
                # url other than image
                # getting content
                #print("-----------------------twitter status---------------------------")
                html = response.text
                soup = b(html)
                if ('i/moments' in u):
                    text = ''
                    moments_text = soup.find('div', {'class': 'MomentCapsuleCover-details'})
                    if moments_text:
                        text = moments_text.text
                else:
                    tweet_status_text = soup.find_all('p', {
                        'class': 'TweetTextSize TweetTextSize--jumbo js-tweet-text tweet-text'})
                    tweet_text = ''
                    for txt in tweet_status_text:
                        if txt:
                            tweet_text = tweet_text + txt.text
                    text = tweet_text
            else:
                #print('------------------------other content--------------------------')

                html = response.text
                text = get_content_from_urls(html)
            content = content + text
        return content


def prep_content(content):
    content = content.replace('"', '')
    content = content.replace("'", '')
    content = " ".join(content.split())

    content = content.encode('utf-8')[:1200]
    if len(str(content)) > 2000:
        content = content[:500]
    return content


def main():
    sql = MySqlUtils('Twitter')
    users = sql.get_data(user_query)
    users_list = [user['user_handle'] for user in users]
    print('Query count {}'.format(len(users)))
    query = 'SELECT tweet_id, urls_contained FROM Twitter.tweet where  user_handle IN (' + ','.join(
        ("'{}'".format(user) for user in users_list)) + ")" + " and related_content IS NULL;"


    # query="SELECT  tweet_id, urls_contained FROM tweet WHERE urls_contained LIKE '%.jpg%';"
    print(query)
    data = sql.get_data(query)
    print("no. of tweet id tweet_id",len(data))
    count=0
    for url in data[10:]:
        count=count+1
        # url_conatined field may have more than 1 url which are seprated by ','
        if not url['urls_contained']:
            query = 'UPDATE tweet SET related_content = "{}" WHERE tweet_id={}'.format('', url['tweet_id'])
        else:
            content = get_content(url)
            if content:
                content = prep_content(content)
                query = 'UPDATE tweet SET related_content = "{}" WHERE tweet_id={}'.format(content, url['tweet_id'])
            else:
                query = 'UPDATE tweet SET related_content = "{}" WHERE tweet_id={}'.format('', url['tweet_id'])

       # print(query)
        print("tweet_id remains",len(data)-count)
        sql.cursor.execute(query)


if __name__ == '__main__':
    main()

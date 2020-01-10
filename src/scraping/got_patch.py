import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, json, re, datetime, sys, \
    http.cookiejar
from pyquery import PyQuery
from lib.GetOldTweets.got3.manager import TweetManager
from lib.GetOldTweets.got3 import models
import json as python_json


def getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy):
    """ Corrected getJsonReponse function change this for new branch

    :param tweetCriteria:
    :param refreshCursor:
    :param cookieJar:
    :param proxy:
    :return:
    """
    urlGetData = ''
    if (tweetCriteria.include_retweets):
        url = "https://twitter.com/i/profiles/show/{}/timeline/tweets?q=%s&src=typd&%smax_position=%s".format(
            tweetCriteria.username)
    elif tweetCriteria.include_replies:
        url = "https://twitter.com/i/profiles/show/{}/timeline/with_replies?q=%s&src=typd&%s".format(
            tweetCriteria.username)
    else:
        url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&%smax_position=%s"
        if hasattr(tweetCriteria, 'username'):
               urlGetData += ' from:' + tweetCriteria.username

    if hasattr(tweetCriteria, 'since'):
        urlGetData += ' since:' + tweetCriteria.since

    if hasattr(tweetCriteria, 'until'):
        urlGetData += ' until:' + tweetCriteria.until

    if hasattr(tweetCriteria, 'querySearch'):
        urlGetData += ' ' + tweetCriteria.querySearch

    if hasattr(tweetCriteria, 'lang'):
        urlLang = 'lang=' + tweetCriteria.lang + '&'
    else:
        urlLang = ''

    if tweetCriteria.include_replies:
        url = url % (urllib.parse.quote(urlGetData), urlLang)
        if refreshCursor:
            url += '&max_position=%s' % refreshCursor
    else:
        url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)

    print(url)

    headers = [
        ('Host', "twitter.com"),
        ('User-Agent', "Chrome/46.0.2490.86"),
        ('Accept', "application/json, text/javascript, */*; q=0.01"),
        ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
        ('X-Requested-With', "XMLHttpRequest"),
        ('Referer', url),
        ('Connection', "keep-alive")
    ]

    if tweetCriteria.include_replies:
        # TODO: To get combined list of tweets and replies, Twitter requires login, so a cookie header is added to authenticate
        # The cookie value is temporary, and keeps changing, so will have to create a selenium job which will run daily and get
        # the cookie, write it in a file. We'll then fetch the value from that file.
        headers.append(('cookie', 'personalization_id="v1_ZMndtKJmovEeRqXnHKwkcA=="; syndication_guest_id=v1%3A150950246428776752; guest_id=v1%3A150950246680303466; _ga=GA1.2.1540401566.1512693959; tfw_exp=0; _gid=GA1.2.532461359.1519290955; dnt=1; ads_prefs="HBESAAA="; kdt=uMwQ417EJ9ZJ5DEP1W0H86lC2OcbVNqytn9TTHW8; _twitter_sess=BAh7CyIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCD2IlTNgAToMY3NyZl9p%250AZCIlYTg5YTNhMmI2Njg1NmRhYjQ1NjQwYWZlNTdkZDcyOTE6B2lkIiViZDA1%250AMjQyZTc3ZmE3N2ViOWRlYmU0MmFkYjVhNWMwYyIJcHJycCIAOgl1c2VybCsJ%250AATAUAifvLw0%253D--b9f8b1079b2b8ed76f2b6e4bbaf4c9ba55ec45b8; remember_checked_on=0; twid="u=950240997216104449"; auth_token=d74f44f1315db858eadc83d14245520808d35922; lang=en; ct0=32f38f18561202357b2e95ee10259fe0; _gat=1'))

    if proxy:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}),
                                             urllib.HTTPCookieProcessor(cookieJar))
    else:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
    opener.addheaders = headers

    try:
        response = opener.open(url)
        jsonResponse = response.read()
    except Exception as e:
        print(e)
        if (tweetCriteria.include_retweets):
            print(
            "Twitter weird response. Try to see on browser: https://twitter.com/i/profiles/show/{}/timeline/tweets?q=%s&src=typd".format(tweetCriteria.username) % urllib.parse.quote(
                urlGetData))
        elif tweetCriteria.include_replies:
            print(
            "Twitter weird response. Try to see on browser: https://twitter.com/i/profiles/show/{}/timeline/with_replies?q=%s&src=typd".format(tweetCriteria.username) % urllib.parse.quote(
                urlGetData))
        else:
            print(
                "Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(
                    urlGetData))
        return

    dataJson = json.loads(jsonResponse.decode())

    return dataJson


@staticmethod
def getTweets(tweetCriteria, receiveBuffer=None, bufferLength=100, proxy=None):
    # TODO: start_date and end_date doesn't get applied when getting retweets or replies

    refreshCursor = ''

    results = []
    resultsAux = []
    cookieJar = http.cookiejar.CookieJar()

    active = True
    while active:
        json_data = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy)

        if not json_data or len(json_data['items_html'].strip()) == 0:
            break

        try:
            refreshCursor = json_data['min_position']
        except KeyError:
            pass

        tweets = PyQuery(json_data['items_html'])('div.js-stream-tweet')

        if len(tweets) == 0:
            break

        for tweetHTML in tweets:
            try:
                tweetPQ = PyQuery(tweetHTML)
                tweet = models.Tweet()
                txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
                retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr(
                    "data-tweet-stat-count").replace(",", ""))
                favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr(
                    "data-tweet-stat-count").replace(",", ""))
                dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))

                if tweetPQ.attr("data-retweeter"):
                    tweet_id = tweetPQ.attr["data-retweet-id"]
                    user_handle = tweetPQ.attr("data-retweeter")
                    retweets_permalink = tweetPQ.attr("data-permalink-path")
                    reply_permalink = ''
                    permalink = '/' + user_handle + '/status/' + tweet_id
                    user_id = tweetPQ('a').attr("data-user-id")
                    usernameTweet = tweetPQ('.js-retweet-text').text()[:-14]
                elif tweetPQ.attr("data-is-reply-to"):
                    tweet_id = tweetPQ.attr["data-tweet-id"]
                    user_handle = tweetPQ.attr("data-screen-name")
                    permalink = tweetPQ.attr("data-permalink-path")
                    retweets_permalink = ''
                    reply_permalink = '/' + user_handle + '/status/' + tweetPQ.attr["data-conversation-id"]
                    user_id = tweetPQ.attr["data-user-id"]
                    usernameTweet = tweetPQ.attr["data-name"]
                else:
                    tweet_id = tweetPQ.attr["data-tweet-id"]
                    user_handle = tweetPQ.attr("data-screen-name")
                    permalink = tweetPQ.attr("data-permalink-path")
                    retweets_permalink = ''
                    reply_permalink = ''
                    user_id = tweetPQ.attr["data-user-id"]
                    usernameTweet = tweetPQ.attr["data-name"]

                geo = ''
                geoSpan = tweetPQ('span.Tweet-geo')
                if len(geoSpan) > 0:
                    geo = geoSpan.attr('title')
                urls = []
                for link in tweetPQ("a"):
                    try:
                        urls.append((link.attrib["data-expanded-url"]))
                    except KeyError:
                        pass
                tweet.id = tweet_id
                tweet.permalink = 'https://twitter.com' + permalink
                tweet.username = usernameTweet

                tweet.text = txt
                tweet.date = datetime.datetime.fromtimestamp(dateSec)
                tweet.formatted_date = datetime.datetime.fromtimestamp(dateSec).strftime("%a %b %d %X +0000 %Y")
                tweet.retweets = retweets
                tweet.favorites = favorites
                tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
                tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
                tweet.geo = geo
                tweet.urls = ",".join(urls)
                tweet.author_id = user_id
                tweet.user_handle = user_handle

                if retweets_permalink:
                    tweet.retweets_permalink = 'https://twitter.com' + retweets_permalink
                else:
                    tweet.retweets_permalink = ''

                if reply_permalink:
                    tweet.reply_permalink = 'https://twitter.com' + reply_permalink
                else:
                    tweet.reply_permalink = ''

                results.append(tweet)
                resultsAux.append(tweet)

                if receiveBuffer and len(resultsAux) >= bufferLength:
                    receiveBuffer(resultsAux)
                    resultsAux = []

                if tweetCriteria.include_replies:
                    refreshCursor = tweetPQ.attr["data-item-id"]

                if tweetCriteria.maxTweets and len(results) >= tweetCriteria.maxTweets:
                    active = False
                    break

            except AttributeError as e:
                print(e)
                pass

    if receiveBuffer and len(resultsAux) > 0:
        receiveBuffer(resultsAux)

    return results

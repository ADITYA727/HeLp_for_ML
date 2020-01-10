import requests
import os,pickle,re
from bs4 import BeautifulSoup as b
import joblib
import lda
import warnings
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
warnings.filterwarnings("ignore")
stops = list(set(stopwords.words('english')))
import tqdm


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

def lda_model(text_list):
    #text1 = ''.join([text for text in text_list])
    text = text_list.split()

    topic_data = {}
    cvectorizer = CountVectorizer(max_features=50, stop_words=stops)
    cvz = cvectorizer.fit_transform(text)
    n_topics = 10
    n_iter = 70
    lda_model = lda.LDA(n_topics=n_topics, n_iter=n_iter)
    lda_model.fit_transform(cvz)

    n_top_words = 30
    topic_summaries = []

    topic_word = lda_model.topic_word_  # get the topic words
    vocab = cvectorizer.get_feature_names()
    topic_dist = topic_word[0]
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
    topic_summaries.append(' '.join(topic_words))
    # print('Topic: {}'.format( ' '.join(topic_words)))
    return ' '.join(topic_words)


def get_content(u,response):

    if 'https://twitter.com' in u:
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
    return text



content=[]
target_names=[]
path='/home/analytics/analytics/data/brand24/'
for filename in os.listdir(path):
    if 'pkl' in path+filename:
        print(filename)
        file=open(path+filename, 'rb')
        content=pickle.load(file)
        for d in tqdm.tqdm(content[:10]):
            try:
                url= re.search("(?P<url>https?://[^\s]+)", d['content']).group("url")
                response = requests.get(url, timeout=1)
                content.append(lda_model(get_content(url, response)))
                target_names.append(filename)
            except Exception as e:
                print("Exception in requesting url", e)
                content.append('')
                target_names.append(filename)

joblib.dump(content,'/home/stealth/Devel/analytics/data/brand24/content_from_url.txt')
joblib.dump(content,'/home/stealth/Devel/analytics/data/brand24/target_names.txt')

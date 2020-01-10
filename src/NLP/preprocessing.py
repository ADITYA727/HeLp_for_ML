import string
import re
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

english_stopwords = nltk_stopwords.words('english')
custom_stopwords = [
    'com', 'today', 'best', 'news', 'twitter', 'watch', 'time', 'instagram', 'video', 'playlist', 'facebook',
    'tatus', 'atus', 'tus', 'youtube', 'youtu', 'life', 'follow', 'retweet', 'retweets', 'like', 'likes', 'hey',
    'get', 'twitte', 'tweeps', 'utm', 'source', 'medium', 'campaign', 'term', 'twi', 'twitt', 'twit'
]
stopwords = english_stopwords + custom_stopwords
tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True, preserve_case=False)
lemma = WordNetLemmatizer()
stemmer = PorterStemmer()
links = re.compile(r"http[s]?://[\s]?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
twitter_pic = re.compile(r'pic.twitter.com\/')


def clean_tweet(tweet, stem=False, lemmatize=False, as_string=True):
    """
    :param tweet:
    :param stem:
    :param lemmatize:
    :return: List of cleaned tokens
    """

    # pyquery cleaning
    corrections = [
        ('http:// ', 'http://'),
        ('https:// ', 'https://'),
        ('http://www. ', 'http://www.'),
        ('https://www. ', 'https://www.'),
        ('pic.twitter.com', 'https://pic.twitter.com')
    ]
    for correction in corrections:
        tweet = tweet.replace(correction[0], correction[1])

    no_hyperlinks = links.sub('', tweet)
    no_hyperlinks = twitter_pic.sub('', no_hyperlinks)
    no_punctuation = re.sub(r'[' + string.punctuation + ']+', ' ', no_hyperlinks)
    no_digits = re.sub("^\d+\s|\s\d+\s|\s\d+$", " ", no_punctuation)

    # Strips handles, removes repeated letters and to_lower
    tokens = tokenizer.tokenize(no_digits)

    # Remove stopwords and remove spaces
    tokens_no_stopwords = [token.strip(' ') for token in tokens if (token not in stopwords) and (not token.isdigit())]

    # Remove any words with 2 or fewer letters
    tokens = [i for i in tokens_no_stopwords if len(i) > 2]
    if stem:
        tokens = map(lambda token: stemmer.stem(str(token)), tokens)

    if lemmatize:
        tokens = [lemma.lemmatize(token) for token in tokens]

    if as_string:
        return ' '.join(tokens)
    else:
        return tokens


#s0 = 'RT @Amila #Test\nTom\'s newly listed Co. &amp; Mary\'s unlisted     Group to supply tech for nlTK.\nh.. $TSLA $AAPL https:// t.co/x34afsfQsh'
#clean_tweet(s0)

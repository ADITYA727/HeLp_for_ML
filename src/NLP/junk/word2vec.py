import tensorflow as tf
import numpy as np
import pandas

WINDOW_SIZE = 2


def import_raw_corpus(filename='../data/output_got.csv'):
    """ Reads output of tweets from GOT library and returns a textblob of all tweets.

    :param filename:
    :return: corpus
    """
    df = pandas.read_csv(filename, delimiter=';', header=0)
    return df.text.astype(str).str.cat(sep=', ')


def preprocess_text(corpus_raw=None):
    """

    :param corpus_raw:
    :return:
    """

    # convert to lower case
    corpus_raw = corpus_raw.lower()

    words = []
    for wrd in corpus_raw.split():
        if wrd != '.': # because we don't want to treat . as a word
            words.extend(wrd.split('.'))

    # so that all duplicate words are removed
    words = set(words)
    vocab_size = len(words)

    word2int = {}
    int2word = {}

    for i, wrd in enumerate(words):
        word2int[wrd] = i
        int2word[i] = wrd

    # raw sentences is a list of sentences.
    raw_sentences = corpus_raw.split('.')
    sentences = []
    for sentence in raw_sentences:
        sentences.append(sentence.split())

    data = []
    for sentence in sentences:
        for word_index, word in enumerate(sentence):
            for nb_word in sentence[max(word_index - WINDOW_SIZE, 0) : min(word_index + WINDOW_SIZE, len(sentence)) + 1] :
                if nb_word != word:
                    data.append([word, nb_word])

    return data, int2word, word2int, vocab_size


# function to convert numbers to one hot vectors
def to_one_hot(data_point_index, vocab_size):
    """

    :param data_point_index:
    :param vocab_size:
    :return:
    """
    temp = np.zeros(vocab_size)
    temp[data_point_index] = 1
    return temp


def get_training_data(data, word2int, vocab_size):
    """

    :param data:
    :param word2int:
    :param vocab_size:
    :return:
    """
    x_train = [] # input word
    y_train = [] # output word

    for data_word in data:
        x_train.append(to_one_hot(word2int[ data_word[0] ], vocab_size))
        y_train.append(to_one_hot(word2int[ data_word[1] ], vocab_size))

    # convert them to numpy arrays
    x_train = np.asarray(x_train)
    y_train = np.asarray(y_train)
    return x_train, y_train

def train(x_train, y_train, vocab_size):
    """

    :param x_train:
    :param y_train:
    :param vocab_size:
    :return:
    """

    # making placeholders for x_train and y_train
    x = tf.placeholder(tf.float32, shape=(None, vocab_size))
    y_label = tf.placeholder(tf.float32, shape=(None, vocab_size))

    EMBEDDING_DIM = 5 # you can choose your own number
    W1 = tf.Variable(tf.random_normal([vocab_size, EMBEDDING_DIM]))
    b1 = tf.Variable(tf.random_normal([EMBEDDING_DIM])) #bias
    hidden_representation = tf.add(tf.matmul(x,W1), b1)

    W2 = tf.Variable(tf.random_normal([EMBEDDING_DIM, vocab_size]))
    b2 = tf.Variable(tf.random_normal([vocab_size]))
    prediction = tf.nn.softmax(tf.add( tf.matmul(hidden_representation, W2), b2))


    sess = tf.Session()
    init = tf.global_variables_initializer()

    saver = tf.train.Saver()

    sess.run(init) #make sure you do this!

    # define the loss function:
    cross_entropy_loss = tf.reduce_mean(-tf.reduce_sum(y_label * tf.log(prediction), reduction_indices=[1]))

    # define the training step:
    train_step = tf.train.GradientDescentOptimizer(0.1).minimize(cross_entropy_loss)

    n_iters = 100000
    # train for n_iter iterations

    for _ in range(n_iters):
        sess.run(train_step, feed_dict={x: x_train, y_label: y_train})
        print('loss is : ', sess.run(cross_entropy_loss, feed_dict={x: x_train, y_label: y_train}))

    vectors = sess.run(W1 + b1)
    saver.save(sess, '../models/politics', global_step=n_iters)

    return vectors



def euclidean_dist(vec1, vec2):
    return np.sqrt(np.sum((vec1-vec2)**2))

def find_closest(word_index, vectors):
    min_dist = 10000 # to act like positive infinity
    min_index = -1
    query_vector = vectors[word_index]
    for index, vector in enumerate(vectors):
        if euclidean_dist(vector, query_vector) < min_dist and not np.array_equal(vector, query_vector):
            min_dist = euclidean_dist(vector, query_vector)
            min_index = index
    return min_index

"""

from sklearn.manifold import TSNE

model = TSNE(n_components=2, random_state=0)
np.set_printoptions(suppress=True)
vectors = model.fit_transform(vectors)

from sklearn import preprocessing

normalizer = preprocessing.Normalizer()
vectors =  normalizer.fit_transform(vectors, 'l2')

print(vectors)

import matplotlib.pyplot as plt


fig, ax = plt.subplots()
print(words)
for word in words:
    print(word, vectors[word2int[word]][1])
    ax.annotate(word, (vectors[word2int[word]][0],vectors[word2int[word]][1] ))
plt.show()
modi
namo
PadmavatiFight
vijayrupani
jayshah
panamapapers
bjp
rss
#HardikExposed
congress
gujratelections


heroku
netlify
DigitalOcean
google compute engine - firebase

"""
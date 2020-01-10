from ekphrasis.classes.segmenter import Segmenter
import re,joblib,os,sys,tqdm
import pandas as pd

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')

def tokenize_hashtags(hashtags):
    seg_eng = Segmenter(corpus="english")
    hash= ' '.join(seg_eng.segment(hashtags) for h in hashtags)
    return hash

def get_dataframe():
    user_data = joblib.load(home + '/../../data/user_data.txt')
    data=pd.DataFrame(list(user_data))
    return data


data=get_dataframe()
hashtags=list(data['hashtags'])

try:
    new_hashtags=joblib.load(home + '/../../data/hashtags.txt')
    hashtags=hashtags[len(new_hashtags):]
except Exception as e:
    print(e)
    new_hashtags=[]

for c,h in enumerate(tqdm.tqdm(hashtags)):
    hash_tag = h.replace('#', '')
    hash_tag = ' '.join(hash_tag.split())
    if len(hash_tag)>1:
        new_hashtags.append(tokenize_hashtags(hash_tag))
    else:
        new_hashtags.append('')
    if c%100==0:
        joblib.dump(new_hashtags, home + '/../../data/hashtags.txt')
joblib.dump(new_hashtags, home + '/../../data/hashtags.txt')

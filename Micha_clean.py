from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import pandas as pd
import numpy as np
import tarfile
import json
import matplotlib.pyplot as plt
from collections import Counter

tf = tarfile.open('geotagged_tweets_20160812-0912.tar.gz', mode='r')
tf.extractall()
counter = 0
tweets_dict = {}
with open('geotagged_tweets_20160812-0912.jsons') as fd:
    for line in fd:
        j_content = json.loads(line)
        tweets_dict[counter] = j_content
        counter += 1
        if counter == 1000: # to keep it  small
            break
            
df = pd.DataFrame.from_dict(tweets_dict, orient='index')
df.head()
df.columns #text and place appear to be most important



import re
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
tok = WordPunctTokenizer()

pat1 = r'@[A-Za-z0-9_]+'
pat2 = r'https?://[^ ]+'
combined_pat = r'|'.join((pat1, pat2))
www_pat = r'www.[^ ]+'
negations_dic = {"isn't":"is not", "aren't":"are not", "wasn't":"was not", "weren't":"were not",
                "haven't":"have not","hasn't":"has not","hadn't":"had not","won't":"will not",
                "wouldn't":"would not", "don't":"do not", "doesn't":"does not","didn't":"did not",
                "can't":"can not","couldn't":"could not","shouldn't":"should not","mightn't":"might not",
                "mustn't":"must not"}
neg_pattern = re.compile(r'\b(' + '|'.join(negations_dic.keys()) + r')\b')

def tweet_cleaner_updated(text):
    soup = BeautifulSoup(text, 'lxml')
    souped = soup.get_text()
    try:
        bom_removed = souped.decode("utf-8-sig").replace(u"\ufffd", "?")
    except:
        bom_removed = souped
    stripped = re.sub(combined_pat, '', bom_removed)
    stripped = re.sub(www_pat, '', stripped)
    lower_case = stripped.lower()
    neg_handled = neg_pattern.sub(lambda x: negations_dic[x.group()], lower_case)
    letters_only = re.sub("[^a-zA-Z]", " ", neg_handled)
    # During the letters_only process two lines above, it has created unnecessay white spaces,
    # I will tokenize and join together to remove unneccessary white spaces
    words = [x for x  in tok.tokenize(letters_only) if len(x) > 1]
    return (" ".join(words)).strip()
    
    
testing = df.text

test_result = []
for t in testing:
    test_result.append(tweet_cleaner_updated(t))
df['text_clean'] = test_result
test_result


from nltk.stem.porter import *
ps = PorterStemmer()
df['text_stemmed'] = df['text_clean'].apply(lambda x: ' '.join([ps.stem(word) for word in x.split() ]))
df['text_stemmed'][:5]


from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()

df['text_lemmed'] = df['text_clean'].apply(lambda x: ' '.join([lmtzr.lemmatize(word,'v') for word in x.split() ]))
df['text_lemmed']

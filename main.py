import ta
import sa

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

df = df[['text', 'place']] #Select only important columns

cnt = Counter()
for i in range(df['place'].shape[0]):
    if df['place'].iloc[i]['country_code'] == 'US':
        cnt[df['place'].iloc[i]['full_name'][-2:]] += 1

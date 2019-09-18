# Import ta (topic analysis) en sa (sentiment analysis)
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
import os
from shapely.geometry import Polygon, MultiPolygon
from descartes import PolygonPatch
from matplotlib import cm
import math

# Function returns dict with tweets from file: "fileName".
def loadTweets(fileName, length):
    counter = 0
    tweets_dict = {}
    with open('geotagged_tweets_20160812-0912.jsons') as fd:
        for line in fd:
            j_content = json.loads(line)
            tweets_dict[counter] = j_content
            counter += 1
            if counter == length: # to keep it  small
                break
    return tweets_dict

def tweets_to_candidates(df):
    """
    This function takes a dataframe of tweets as input. 
    It select entries that react to either Trump, Hillary or both.
    It then places the tweet text of the  entries in the corresponding dictionary.
    This is the tweet text as a list entry with the tweeters state as key.
    The output is a dict with 3 dicts (both, trump, hillary) with all states as keys and the tweets from that state as valeus.
    
    """
    both_dict = {}
    trump_dict = {}
    hillary_dict ={}
    for i in range(df['text'].shape[0]):
        if df['place'].iloc[i]['country'] == 'United States':
            if '@realDonaldTrump' and '@HillaryClinton' in df['text'].iloc[i]:
                text = df['text'].iloc[i]
                state = df['place'].iloc[i]['full_name'][-2:]
                both_dict.setdefault(state,[]).append(text)
            elif '@realDonaldTrump'in df['text'].iloc[i]:
                text = df['text'].iloc[i]
                state = df['place'].iloc[i]['full_name'][-2:]
                trump_dict.setdefault(state,[]).append(text)
            elif '@HillaryClinton' in df['text'].iloc[i]:
                text = df['text'].iloc[i]
                state = df['place'].iloc[i]['full_name'][-2:]
                hillary_dict.setdefault(state,[]).append(text)
    return {'both':both_dict, 'trump':trump_dict, 'hillary': hillary_dict}


def main():
    tweets_dict = loadTweets('geotagged_tweets_20160812-0912.jsons', 1000)
    df = pd.DataFrame.from_dict(tweets_dict, orient='index')
    df = df[['text', 'place']]

    dirtyTextDict = df.text
    cleanTestDict = []
    for t in dirtyTextDict:
        cleanTestDict.append(sa.tweet_cleaner_updated(t))
    df['text_clean'] = cleanTestDict
    sa.lemmer(df)
    print(df['text_clean'])

    # Count occurences per state.
    cnt = Counter()
    for i in range(df['place'].shape[0]):
        if df['place'].iloc[i]['country_code'] == 'US':
            cnt[df['place'].iloc[i]['full_name'][-2:]] += 1

    cnt_df = pd.DataFrame.from_dict(cnt, orient='index')
    cnt_df = cnt_df.drop("SA")[0]


if __name__ == "__main__":
    main()





    # # Next step is to make a map visualization of the distribution
    # S_DIR = 'states_21basic/'
    # MAXIMUM = cnt_df.max() # get the highest value state
    # BLUE = '#5599ff'
    # cmap = plt.get_cmap('YlOrRd') # Choose a colormap to be used to color
    #
    # with open(os.path.join(S_DIR, 'states.json')) as rf:
    #     data = json.load(rf)
    #
    # fig = plt.figure()
    # ax = fig.gca()
    # for feature in data['features']:
    #     geometry = feature['geometry']
    #
    #     # Convert population to a proportion of the maximum value
    #     name = feature['properties']['STATE_ABBR']
    #     frequency_prop = math.sqrt((cnt[name]/MAXIMUM))
    #
    #     if geometry['type'] == 'Polygon':
    #         poly = geometry
    #         ppatch = PolygonPatch(poly, fc=cmap(frequency_prop), ec=BLUE,  alpha=0.5, zorder=2)
    #         ax.add_patch(ppatch)
    #
    #     elif geometry['type'] == 'MultiPolygon':
    #         for polygon in geometry['coordinates'][0]:
    #             poly = Polygon(polygon)
    #             ppatch = PolygonPatch(poly, fc=cmap(frequency_prop), ec=BLUE, alpha=0.5, zorder=2)
    #             ax.add_patch(ppatch)
    #     else:
    #         print('Don\'t know how to draw :', geometry['type'])
    #
    # ax.axis('scaled')
    # plt.axis('off')
    # plt.show()

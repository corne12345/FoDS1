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
def loadTweets(fileName):
    counter = 0
    tweets_dict = {}
    with open('geotagged_tweets_20160812-0912.jsons') as fd:
        for line in fd:
            j_content = json.loads(line)
            tweets_dict[counter] = j_content
            counter += 1
            if counter == 1000: # to keep it  small
                break
    return tweets_dict


def main():
    tweets_dict = loadTweets('geotagged_tweets_20160812-0912.jsons')
    df = pd.DataFrame.from_dict(tweets_dict, orient='index')
    df = df[['text', 'place']]

    dirtyTextDict = df.text
    cleanTestDict = []
    for t in dirtyTextDict:
        cleanTestDict.append(sa.tweet_cleaner_updated(t))
    df['text_clean'] = cleanTestDict

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

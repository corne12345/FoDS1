from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import pandas as pd
import numpy as np
import tarfile
import json
import matplotlib.pyplot as plt
from collections import Counter
import re
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import *
from pprint import pprint
from nltk.probability import FreqDist
from nltk.classify.util import apply_features
from nltk import NaiveBayesClassifier

word_features = []

# Function that first rewrites certain patterns in a text to valid words and
# then tokenizes all the words the text.
def tweet_cleaner_updated(text):
    tok = WordPunctTokenizer()

    # Regexes used to rewrite certain patterns to valid words.
    pat1 = r'@[A-Za-z0-9_]+|#[A-Za-z0-9_]+'
    pat2 = r'https?://[^ ]+'
    combined_pat = r'|'.join((pat1, pat2))
    www_pat = r'www.[^ ]+'
    negations_dic = {"isn't":"is not", "aren't":"are not", "wasn't":"was not", "weren't":"were not",
                    "haven't":"have not","hasn't":"has not","hadn't":"had not","won't":"will not",
                    "wouldn't":"would not", "don't":"do not", "doesn't":"does not","didn't":"did not",
                    "can't":"can not","couldn't":"could not","shouldn't":"should not","mightn't":"might not",
                    "mustn't":"must not"}
    neg_pattern = re.compile(r'\b(' + '|'.join(negations_dic.keys()) + r')\b')

    # Tokenize words.
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

def stemmer(df):
    ps = PorterStemmer()
    sentenceList = df['text_clean'].apply(lambda x: ' '.join([ps.stem(word) for word in x.split() ]))
    wordsList = sentenceList.apply(lambda x: x.split())
    df['text_stemmed'] = wordsList

def lemmer(df):
    lmtzr = WordNetLemmatizer()
    sentenceList = df['text_clean'].apply(lambda x: ' '.join([lmtzr.lemmatize(word,'v') for word in x.split() ]))
    wordsList = sentenceList.apply(lambda x: x.split())
    df['text_lemmed'] = wordsList

# Get the separate words in tweets
# Input:  A list of tweets
# Output: A list of all words in the tweets
def get_words_in_tweets(df_train, type):
    tweets = df_train['text_' + type]
    all_words = []
    for words in tweets:
        all_words.extend(words)

    return all_words

# Create a dictionary measuring word frequencies
# Input: the list of words
# Output: the frequency of those words apearing in tweets
def get_word_features(wordlist):
    # print(wordlist)
    wordlist = FreqDist(wordlist)
    word_features = wordlist.keys()
    # print ("Word frequency list\n")
    # pprint(wordlist)
    return word_features

# Construct our features based on which tweets contain which word
def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

# Function that returns a NaiveBayesClassifier, trained with the movie_reviews datasetself.
# TODO: TRAINT MOMENTEEL MET HELE DATASET EN TEST NIET!!
def get_trained_classifier():
    df = pd.read_csv("sentiment.csv")

    cleanTestDict = []
    for text in df['text']:
        cleanTestDict.append(tweet_cleaner_updated(text))
    df['text_clean'] = cleanTestDict

    lemmer(df)
    stemmer(df)

    df_final = []
    type = 'lemmed'
    global word_features
    word_features = get_word_features(get_words_in_tweets(df, type))
    for index, row in df.iterrows():
        if row.sentiment == 0:
            df_final.append((row['text_' + type],'negative'))
        elif row.sentiment == 4:
            df_final.append((row['text_' + type],'positive'))

    training_set = apply_features(extract_features, df_final)
    classifier = NaiveBayesClassifier.train(training_set)
    classifier.show_most_informative_features()
    return classifier

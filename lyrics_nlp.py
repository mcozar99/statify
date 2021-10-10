"""
Analisys of the topics treated by artists on their playlist, using BERTopic
Only for English and Spanish!!!!!
"""
import re

import pandas as pd
import numpy as np
from playlist_dataframe_builder import get_playlist_dataframe
import requests
import lyricsgenius
from keys import genius_token
from bs4 import BeautifulSoup
from gensim.parsing.preprocessing import remove_stopwords, STOPWORDS
from nltk.corpus import stopwords
from bertopic import BERTopic


genius = lyricsgenius.Genius(access_token=genius_token)

# For later purposes
replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )

# 1st step get playlist, request to genius
def get_lyrics(artist):
    """
    Gets lyrics list from all the songs of a playlist given
    :param artist: name of the artist to explore
    :return: df with lyrics column
    """
    df = get_playlist_dataframe('This is %s'%artist)
    texts = []
    for index, row in df.iterrows():
        try:
            lyrics = genius.search_song(row.Title, row.Artist).lyrics
            # A little bit of cleaning
            lyrics = re.sub("[\(\[].*?[\)\]]", "", lyrics.lower())
            for a, b in replacements:
                lyrics = lyrics.replace(a, b)
            lyrics = remove_stopwords(lyrics, stopwords=STOPWORDS)
            lyrics = remove_stopwords(lyrics, stopwords=stopwords.words('spanish'))
            texts.append(lyrics)
        except:
            print('%s failed'%row.Title)
            df = df.drop(index)
    df['lyrics'] = texts
    return df

def lyrics_analysis(artist, figure=True):
    """
    Non-Supervised Technique for analysis of artist lyrics
    :param artist: subject to analyze
    :param figure: plots a figure of the topic map, default True
    :return: clustering figure with topics mentioned and list of topics
    """
    df = get_lyrics(artist)
    #Declare model
    bertopic = BERTopic(language='multilingual', verbose=True, min_topic_size=5)

    clusters, probs = bertopic.fit_transform(df.lyrics.values)
    df['cluster'] = clusters
    if figure:
        try:
            bertopic.visualize_term_rank().write_html('cluster_representation/term_rank_%s.html' % artist)
            bertopic.visualize_hierarchy().write_html('cluster_representation/hierarchy_%s.html'%artist)
        except:
            pass
    df.to_excel('playlists/%s.xls'%artist, float_format="%.2f", index=False)

lyrics_analysis('Kanye West')
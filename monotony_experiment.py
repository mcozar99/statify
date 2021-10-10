"""
Experiment to know which are the most and the least innovative artists in the top
"""
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from keys import ID, ID_SECRET, redirect_uri, scope
import requests
from bs4 import BeautifulSoup
from collections import Counter
import os
import plotly.graph_objects as go
import plotly.express as px
from subprocess import call
from playlist_clustering import cluster_playlist

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))

def do_experiment(n, BASE_URL = 'https://kworb.net/spotify/country/global_weekly_totals.html', country = 'Global'):
    """
    Makes experiment and builds a dataframe with the average features of top n artists
    :param n: number of artists to analyze
    :param BASE_URL: URL to fetch content, default is the global weekly list, checkout the page to obtain your own country list
    :param country: Just in order to save the excel
    :return: dataframe with characteristics of artists and excel on experiments directory
    """
    # GET the global most listened songs since 2013 from this page
    artists = []

    home_page= BASE_URL
    hsession = requests.Session()
    hresponse = hsession.get(home_page)
    soup=BeautifulSoup(hresponse.content.decode('utf-8'), "lxml")
    # Filter query
    tracks_and_artists = soup.findAll('a')
    # Extract Artist Names
    for item in tracks_and_artists:
        try:
            if 'artist' in item['href']:
                artists.append(item.contents[0])
        except:
            pass

    # We have more than 1000 artists, so we clean up a little bit getting the n most common
    artists = list(dict(Counter(artists).most_common(n)).keys())

    # Define parameters for our new DataFrame, composed by this average metrics of the artists plus the number of clusters
    avg_danceability, avg_energy, avg_key, avg_speechiness, avg_acousticness, \
    avg_instrumentalness, avg_liveness, avg_valence, versatility_scores = ([] for i in range(9))

    # Build data for every artist
    for artist in artists:
        df = cluster_playlist('This is: %s'%artist, save=False, onlySpotify=True)
        if not (df is None):
            avg_danceability.append(df['danceability'].mean())
            avg_energy.append(df['energy'].mean())
            avg_key.append(df['key'].mean())
            avg_speechiness.append(df['speechiness'].mean())
            avg_acousticness.append(df['acousticness'].mean())
            avg_instrumentalness.append(df['instrumentalness'].mean())
            avg_liveness.append(df['liveness'].mean())
            avg_valence.append(df['valence'].mean())
            # The number of clusters is our metric for measuring versatility
            versatility_scores.append(Counter(df.cluster).__len__())
        else:
            # Protection against errors
            avg_danceability.append(None)
            avg_energy.append(None)
            avg_key.append(None)
            avg_speechiness.append(None)
            avg_acousticness.append(None)
            avg_instrumentalness.append(None)
            avg_liveness.append(None)
            avg_valence.append(None)
            # The number of clusters is our metric for measuring versatility
            versatility_scores.append(None)

    # Build DataFrame and save it
    results = pd.DataFrame({'artist' : artists, 'versatility' : versatility_scores, 'avg_danceability' : avg_danceability,
                            'avg_energy' : avg_energy, 'avg_key' : avg_key, 'avg_speechiness' : avg_speechiness,
                            'avg_acousticness' : avg_acousticness, 'avg_instrumentalness' : avg_instrumentalness,
                            'avg_liveness' : avg_liveness, 'avg_valence' : avg_valence})

    print(results)
    # Delete artists who hasn´t got a playlist
    results = results.dropna()
    # Save it to excel for later purposes
    results.to_excel('experiment/%stop%s.xls'%(country, n), float_format="%.2f", index=False)

def get_maxmin_artist_by_feature(excel):
    """
    Gets Top and Bottom Artist for every category
    :param excel: datasheet that we want to analyze, result of do_experiment function (only introduce the name)
    :return: Dataframe with the data
    """
    df = pd.read_excel('experiment/%s.xls'%excel)
    result = pd.DataFrame(columns=['max', 'min'])
    for stat in df.columns:
        # No max and min artist
        if stat == 'artist':
            pass
        else:
            aux1 = df['%s'%stat].max()
            aux2 = df['%s'%stat].min()
            max = df[df['%s'%stat] == aux1].iloc[0]['artist']
            min = df[df['%s'%stat] == aux2].iloc[0]['artist']
            result.loc['%s'%stat] = (max, min)
    result.to_excel('experiment/%s_stats.xls'%excel)

def plot_stat(stat, tops='all'):
    """
    Plot an histogram of several tops or everyone in one statistic
    :param stat: the one that you want to plot
    :param tops: list of tops you want to plot, default all plots everyone
    :return: an histogram comparing
    """
    # Get the files needed
    if tops=='all':
        dirs = os.listdir('experiment')
        dirs.remove('histograms')
        for dir in dirs:
            if '_stats' in dir:
                dirs.remove(dir)
    else:
        dirs = tops
    # Get all dfs and plot them, first declare figure
    fig = go.Figure()
    try:
        for file in dirs:
            df = pd.read_excel('experiment/%s'%file)
            if 'Global' in file:
                fig.add_trace(go.Histogram(x=df['%s'%stat], histfunc='avg', name=file.replace('.xls', ''), marker_color=px.colors.qualitative.Set2[0]))
                fig.add_trace(go.Scatter(
                              x=[df['%s'%stat].mean(), df['%s'%stat].mean()],
                              y=[0,100],
                              line=dict(width=4, dash='dashdot', color=px.colors.qualitative.Set2[1]),
                              name=file.replace('.xls', '%s'%stat)))

            else:
                fig.add_trace(go.Scatter(
                    x=[df['%s' % stat].mean(), df['%s' % stat].mean()],
                    y=[0, 100],
                    line=dict(width=4, dash='dashdot'),
                    name=file.replace('.xls', '%s' % stat)))


    except:
            # Some file is wrong
            print('ERROR: check your files included')
            return

    # Custom the figure
    fig.update_layout(
        title_text='%s comparison between tops'%stat,  # title of plot
        xaxis_title_text='Value',  # xaxis label
        yaxis_title_text='Count',  # yaxis label
        bargap=0.1
    )

    if not os.path.exists('experiment/histograms'):
        call('mkdir experiment/histograms', shell=True)
    fig.write_html('experiment/histograms/%s.html'%stat)



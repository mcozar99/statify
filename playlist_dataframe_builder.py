"""
This module extracts a playlist features given a name
"""
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from keys import ID, ID_SECRET, redirect_uri, scope
from subprocess import call
import re
import xlwt
import matplotlib.pyplot as plt
from collections import Counter
import itertools
from datetime import timedelta


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))


def get_playlist_dataframe(playlist, save=False, displayResults=False, onlySpotify=False):
    """
    Returns every track of a playlist given the name
    :param playlist: name of the playlist
    :param save: save dataframe in excel file. Default=False
    :param onlySpotify: bool that activated returns null if spotify is not the owner of the playlist
    :return: a dataframe with the essential data of every track
    """

    # Search Index of the playlist
    try:
        data = sp.search(q=playlist, type='playlist')['playlists']['items'][0]
        print('Getting playlist %s made by %s with ID %s'%(data['name'],data['owner']['display_name'],data['id']))
        playlist_name = re.sub('[^A-Za-z0-9]+', '', data['name'])
    except:
        print('ERROR 404: Playlist not found')
        return

    # Only for some experiments, if spotify is not the owner returns null
    if onlySpotify:
        if 'Spotify' != data['owner']['display_name']:
            print('Spotify doesn´t have playlist %s'%data['name'])
            return None

    # Loop for saving every track
    results = sp.playlist_items(data['id'])
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    # Builds the dataframe with essential aspects of the tracks on the playlist
    titles, artists, popularities, ids = ([] for i in range(4))
    for item in tracks:
        try:
            item = item['track']
            try:
                # Filter possible podcasts in playlists (like in AC/DC)
                if 'track' in item['type']:
                    titles.append(item['name'])
                    artists.append(item['artists'][0]['name'])
                    popularities.append(item['popularity'])
                    ids.append(item['id'])
            except:
                pass
        except:
            pass

    df = pd.DataFrame({'Id' : ids, 'Title': titles, 'Artist': artists, 'Popularity': popularities})

    # Extract the features for every song on the playlist
    features=[]
    i=0
    while i < df.__len__():
        feature = sp.audio_features(df.Id.iloc[i])[0]
        if not (feature is None):
            features.append(feature)
            i += 1
        else:
            df = df.drop(i)
            i = i - 1
    features = pd.DataFrame(features).drop(['time_signature', 'duration_ms', 'analysis_url', 'track_href', 'uri', 'id', 'type'], axis=1)

    # Merge both Dataframes
    df = pd.concat([df, features], axis=1)

    # Save it on an Excel if true
    if save:
        if not os.path.exists('playlists'):
            call('mkdir playlists', shell=True)
        df.to_excel('playlists/%s.xls'%playlist_name, float_format="%.2f", index=False, startrow=2, startcol=2)
        print('Saved')

    # Display results
    if displayResults:
        print(df)
    return df




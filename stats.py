"""
This module gets top x artists and songs listened by the current user
"""
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from keys import ID, ID_SECRET, redirect_uri, scope
from collections import Counter
from datetime import timedelta


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))

def top_artists(term, limit=50):
    """Gets top artists and genders in a term:
    Parameters: term: can be 'short_term', 'medium_term' or 'long_term', indicates how long do we count
                limit: indicates how many artists do we show, max limit of 50"""
    data = sp.current_user_top_artists(time_range=term, limit=limit)['items']
    ids = []
    names = []
    genres = []
    popularity = []
    for item in data:
        ids.append(item['id'])
        names.append(item['name'])
        genres.append(item['genres'])
        popularity.append(item['popularity'])
    ranking = pd.DataFrame({'name':names, 'popularity':popularity})
    print('Your %s ranking is:'%term)
    print(ranking)
    top_genres = []
    for genre in genres:
        top_genres += genre
    top_genres = Counter(top_genres)
    df = pd.DataFrame.from_dict(top_genres, orient='index', columns=['Artists']).sort_values(by='Artists', ascending=False)
    print('Top 10 Favourite Genres Based on Your Artists:')
    print(df.head(10))
    print('Average popularity of your Favourite Artists: %s'%ranking.popularity.mean())
    return data, ranking

def top_songs(term, limit=50):
    """Gets top songs and genders in a term:
    Parameters: term: can be 'short_term', 'medium_term' or 'long_term', indicates how long do we count
    limit: indicates how many artists do we show, max limit of 50"""
    data = sp.current_user_top_tracks(time_range=term, limit=limit)['items']
    titles, artists, popularities, durations = ([] for i in range(4))
    for item in data:
        titles.append(item['name'])
        artists.append(item['artists'][0]['name'])
        popularities.append(item['popularity'])
        durations.append(timedelta(seconds=round(item['duration_ms']/1000)))
    ranking = pd.DataFrame({'Title' : titles, 'Artist' : artists, 'Duration': durations, 'Popularity': popularities})
    print('Your ranking:')
    print(ranking)
    print('Artist with most appearances is %s with %s songs on top'
          %(Counter(ranking.Artist.values).most_common(1)[0][0],
            Counter(ranking.Artist.values).most_common(1)[0][1]))
    print('Average popularity of your top: %s'%ranking.Popularity.mean())
    return data, ranking

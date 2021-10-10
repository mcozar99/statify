"""
This module is created to help you to understand how are the songs of your pñaylist situated on a 2D Map according
to their features. First we will load our playlist and afterwards we will plot them after reducing dimensionality
We will cluster them to understand how they are distributed
"""
import pandas as pd
import hdbscan
import umap.umap_ as umap
from playlist_dataframe_builder import get_playlist_dataframe
import plotly.express as px
import os
from subprocess import call


def cluster_playlist(playlist_name, save=True, onlySpotify=False):
    """
    CLusters playists according to their features with HDBSCAN and UMAP. Interactive representation of topics
    :param playlist_name: playlist you want to cluster
    :param save: If True saves the interactive in HTML, otherwise only returns a dataframe with the cluster
    :param onlySpotify: only for some experiments, doesn´t return anything if spotify isn´t owner of the playlist
    :return: a dataframe with the clusters and the playlist data
    """
    # Load df from playlist
    df = get_playlist_dataframe(playlist_name, onlySpotify=onlySpotify)

    # Only for some experiments
    if df is None:
        return None

    # Prepare HDBSCAN clusterer plus preparing song texts and grouping points
    clusterer = hdbscan.HDBSCAN(cluster_selection_method='eom', approx_min_span_tree=True, gen_min_span_tree=True, min_samples=None)
    points = df.drop(['Id', 'Title', 'Artist', 'Popularity', 'tempo', 'loudness', 'mode'], axis=1)
    points = points.to_numpy()
    songs = df.Title + ', ' + df.Artist

    # Clustering
    clusterer.fit(points)


    # Reduce dimensions with UMAP
    umap_model = umap.UMAP(n_components=2, min_dist=0.0).fit(points)
    transformed_points = umap_model.transform(points)

    
    # Group results into a new DataFrame
    results = pd.DataFrame({'Text' : songs, 'X' : transformed_points[:,0], 'Y' : transformed_points[:,1], 'label' : clusterer.labels_})
    # Interactive Plotting
    fig = px.scatter(results, x="X", y="Y", color="label", hover_data=['Text'],
                     title='Distribution of tracks by feature in playlist %s'%playlist_name)

    # Saving into HTML files if save == True
    if save:
        if not os.path.exists('cluster_representation'):
            call('mkdir cluster_representation', shell=True)
        fig.write_html('cluster_representation/%s.html'%playlist_name.replace(' ', ''))

    # Adds cluster list to the dataframe
    df['cluster'] = clusterer.labels_
    # Return
    return df


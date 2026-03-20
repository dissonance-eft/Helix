import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json

# Load data
df = pd.read_csv(r'C:\Users\dissonance\Desktop\Helix\labs\datasets\music\metadata\spotify.csv')

# 1. Identify top artists and tracks
top_artists = df['Artist Name(s)'].value_counts().head(20).to_dict()
top_tracks = df['Track Name'].value_counts().head(10).to_dict()

# 2. Extract structural features
features = ['Danceability', 'Energy', 'Loudness', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo']
data = df[features].copy()
data = data.dropna()

# Normalize
scaler = StandardScaler()
scaled_data = scaler.fit_transform(data)

# Cluster for modes
kmeans = KMeans(n_clusters=6, random_state=42)
data['Mode_Cluster'] = kmeans.fit_predict(scaled_data)

# Join back or just use the data
df = df.iloc[data.index].copy()
df['Mode_Cluster'] = data['Mode_Cluster']

# Compute averages per cluster to identify modes
modes = df.groupby('Mode_Cluster')[features].mean().to_dict('index')

# Identify invariants (features with low variance or consistent ranges)
invariants = {
    'Tempo': {'mean': df['Tempo'].mean(), 'std': df['Tempo'].std()},
    'Energy': {'mean': df['Energy'].mean(), 'std': df['Energy'].std()},
    'Instrumentalness': {'mean': df['Instrumentalness'].mean(), 'std': df['Instrumentalness'].std()}
}

# Identify outliers (top 5 by distance from cluster center is complex, let's just do top/bottom extremes)
outliers = {
    'highest_complexity_proxy': df.sort_values(by='Instrumentalness', ascending=False).head(5)[['Track Name', 'Artist Name(s)', 'Instrumentalness']].to_dict('records'),
    'highest_energy': df.sort_values(by='Energy', ascending=False).head(5)[['Track Name', 'Artist Name(s)', 'Energy']].to_dict('records'),
    'highest_chaos_proxy': df.sort_values(by='Tempo', ascending=False).head(5)[['Track Name', 'Artist Name(s)', 'Tempo']].to_dict('records'),
    'highest_minimalism_proxy': df.sort_values(by='Energy', ascending=True).head(5)[['Track Name', 'Artist Name(s)', 'Energy']].to_dict('records')
}

# Mapping preferences across axes (Simplified logic)
# Structure (Higher energy/danceability) vs Atmosphere (Higher acousticness/instrumentalness)
df['Structure_Axis'] = (df['Energy'] + df['Danceability']) / 2
df['Atmosphere_Axis'] = (df['Acousticness'] + df['Instrumentalness']) / 2

# Repetition (Instrumentalness) vs Progression (Speechiness - proxy for lyrics/linear delivery)
# Note: This is an assumption-based proxy
df['Repetition_Axis'] = df['Instrumentalness']
df['Progression_Axis'] = df['Speechiness']

results = {
    'top_artists': top_artists,
    'modes': modes,
    'invariants': invariants,
    'outliers': outliers,
    'axes_means': {
        'Structure vs Atmosphere': {'Structure': df['Structure_Axis'].mean(), 'Atmosphere': df['Atmosphere_Axis'].mean()},
        'Repetition vs Progression': {'Repetition': df['Repetition_Axis'].mean(), 'Progression': df['Progression_Axis'].mean()},
        'Energy vs Control': {'Energy': df['Energy'].mean(), 'Control': 1 - df['Valence'].mean()}, # Control as inverse of valence (unpredictability/unrestrained emotion)
    }
}

print(json.dumps(results, indent=2))


from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from scipy.spatial import distance

app = Flask(__name__)

data = pd.read_csv(r"/Users/sarthak/Downloads/My_Minor2_updated//data.csv")
data.head()

data = data.drop(columns=["key","mode","time_signature"])
df = data.copy()
df = df.drop(columns=["artist_name","track_name"])

col = ['acousticness', 'danceability', 'duration_ms',
       'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness',
       'tempo', 'valence']
scaler = StandardScaler()
df[col] = scaler.fit_transform(df[col])

df["name"] = data["track_name"]
df["artist"] = data["artist_name"]

df_2 = df.drop(columns=["artist","name"])
def find_song(word, artist):
    a = 0
    b = 0
    for i, track_name in enumerate(data["track_name"]):
        artist_name = data["artist_name"][a]
        if isinstance(track_name, str) and isinstance(artist_name, str):
            if word.lower() in track_name.lower() and artist.lower() in artist_name.lower():
                print("Song Name: ", track_name, ", Artists: ", artist_name)
                b += 1
        a += 1
    if b == 0:
        print("Nothing found. Please try something else :)")


def sim_track_find(word, artist):
    a = 0
    b = 0
    song = []
    indexes = []
    for i, track_name in enumerate(data["track_name"]):
        artist_name = data["artist_name"][a]
        if isinstance(track_name, str) and isinstance(artist_name, str):
            if word.lower() in track_name.lower() and artist.lower() in artist_name.lower():
                song.append(df_2.loc[a:a+1].values)
                indexes.append(a)
                b += 1
        a += 1
    if b == 0:
        print("Nothing found. Please try something else :)")
        return 0
        
    return song[0][0], indexes[0]


def similar_tracks(number, song="", artist=""):
    result = []  # List to store similar songs

    if sim_track_find(song, artist) == 0:
        return result  # Return an empty list if no similar tracks found
    else:
        x, index = sim_track_find(song, artist)
        
    # Calculate cosine distance for similarity
    p = []
    count = 0
    for i in df_2.values:
        p.append([distance.cosine(x, i), count])
        count += 1
    p.sort()
    song_names = df["name"]
    artist_names = df["artist"]

    similar_songs_info = []
    for i in range(1, number + 1):
        similar_song_name = song_names[p[i][1]]
        similar_artist_name = artist_names[p[i][1]]
        similar_songs_info.append((similar_song_name, similar_artist_name))

    # Append similar song details to the result list
    result.extend(similar_songs_info)

    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        song = request.form['song']
        artist = request.form['artist']
        num = int(request.form.get('num', False))
        result = similar_tracks(num, song, artist)
        
        # Check if no similar tracks found
        if not result:
            result = "No similar tracks found. Please try different inputs."
        
        return render_template('index.html', result=result)
    
    return render_template('index.html', result=None)

if __name__ == '__main__':
     app.run(debug=True)
import re
import spotipy
import time
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
from datetime import datetime

now_day = datetime.now().strftime("%d-%m-%y")
app = Flask(__name__)

def extract_song_and_artist(song_string):
    # Регулярное выражение для извлечения информации
    tracks = song_string.replace('.mp4', ".mp3").split(".mp3")[:len(song_string.split(".mp3"))-1] #последний элемент пустой, убираем его
    splitted_songs = []
    for line in tracks:
        pattern = r"\d{1,2}:\d{2}\s(.+?)\s-\s(.+)"
        splitted_songs.append(re.findall(pattern, line))
    df = pd.DataFrame(splitted_songs)
    df.dropna(inplace=True)
    return df.values

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'insert_app_secret_key'
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oath().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    try:
        token_info = create_spotify_oath().get_access_token(code)
        session[TOKEN_INFO] = token_info
    except Exception as e:
        print('Error retrieving token:', e)
        return redirect(url_for('login'))
    return redirect(url_for('put_song_names', external=True))

@app.route('/putSongsName', methods=['GET', 'POST'])
def put_song_names():

    try:
        token_info = get_token()
    except:
        print('user not logged in')
        return redirect('/')

    #if request.method == 'GET':
        #return render_template('index.html')
    if request.method == 'POST':
        data = request.form.to_dict()
        songs = str(data['songs']) #получаем список из html формы
        album_name = str(data['album'])
        track_list = extract_song_and_artist(songs) #вытаскиваем треки и исполнителей
        #track_list = track_list[:len(track_list)-2] #в возвращаемом списке последний элемент пустой, избавляемся от него


        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_id = sp.current_user()['id']

        mnemonic_playlist_id = None
        infinite_playlist_id = None

        current_playlists = sp.user_playlists(user_id)['items']
        for playlist in current_playlists:
            if (playlist['name'] == album_name):
                return "Playlist has alredy been created"
            elif (playlist['name'] == 'Mnemonic infinite'):
                infinite_playlist_id = playlist['id']
                tracks_infinite = sp.playlist_items(infinite_playlist_id)
                infinite_song_uris = []
                for track in tracks_infinite['items']:
                    infinite_song_uris.append(track['track']['uri'])





                if not mnemonic_playlist_id:
            new_playlist = sp.user_playlist_create(user_id, album_name, True) # создаем новый плейлист
            mnemonic_playlist_id = new_playlist['id'] # получаем id плейлиста

            song_uris = []
            for song in track_list:
                song_uri = sp.search(q=(song[0][0]+" "+song[0][1]), type='track')['tracks']['items'][0]['uri']
                song_uris.append(song_uri)

            sp.user_playlist_add_tracks(user_id, mnemonic_playlist_id, song_uris, None)
            if infinite_playlist_id:
                infinite_song_uris_set = set(infinite_song_uris)
                new_song_uris = [item for item in song_uris if item not in infinite_song_uris_set]
                if len(new_song_uris) > 0:
                    sp.user_playlist_add_tracks(user_id, infinite_playlist_id, new_song_uris, None)

            mnemonic_playlist_id = None
            return render_template('index.html')

    return render_template('index.html')



def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', external = False))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oath()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oath():
    return SpotifyOAuth(client_id = "insert_client_id",
                        client_secret = "insetr_client_secret",
                        redirect_uri = url_for('redirect_page', _external= True),
                        scope = 'playlist-read-private user-library-read, playlist-modify-public, playlist-modify-private')

app.run(debug=True)

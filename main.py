import spotipy
import time
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
from datetime import datetime

now_day = datetime.now().strftime("%Y-%m-%d")
app = Flask(__name__)

data = """1. 1:00 Bloodmasta Cut,k-sette,Hoody - Alice In Wonderland.mp3
 2. 2:08 Jean Tonique - too bad.mp3
 3. 5:10 Inner Wave - Schemin.mp3
 4. 7:17 Wet Leg - Chaise Longue.mp3
 5. 10:30 Nymano,JK the sage - Sunday Mornings.mp3
 6. 12:10 Phil Tyler,Stasevich - Just Slam.mp3
 7. 14:53 Enzzy Beatz - all cats are beautiful.mp3
 8. 16:28 Bluewerks,Maple Syrup - Sunbeams.mp3
 9. 18:52 Royel Otis - Foam.mp3
 10. 21:52 Tour De Manège,Ours Samplus - Big Shit.mp3
 11. 24:32 90sFlav - Drawup.mp3
 12. 26:20 Parks, Squares And Alleys,Young And Dramatic - Passenger.mp3
 13. 29:36 Marcoca,Nice Guys - I'm About to Disappear.mp3
 14. 33:30 Tokyo Tea Room,Juravlove - Eat You Alive (Juravlove Remix).mp3
 15. 39:12 Jazzinuf - Hugging You (Quietly).mp3
 16. 40:58 Feng Suave - Tomb for Rockets.mp3
 17. 45:12 Miel De Montagne - Relax le plexus.mp3
 18. 48:20 Homeshake - Vacuum.mp3
 19. 51:12 Her's - Cool with You.mp3
 20. 57:20 Ed O.G - I'm Laughin'.mp3
 21. 1:01:24 Kowloon - Life in Japan.mp3
 22. 1:05:40 Phairo - Pelican.mp3
 23. 1:09:28 Ariel Pink - Another Weekend.mp3
 24. 1:13:32 Easy Life - daydreams.mp3
 25. 1:16:00 Monma - Sneakers.mp3
 26. 1:18:24 Goth Babe - Swami's.mp3"""

data_splitted = data.split(".mp3")

clean_splitted = []
for line in data_splitted:
    clean_splitted.append(line.strip('\n '))
track_names = []
artists = []
for line in clean_splitted:
    track_names.append(line[line.find(' - ') + 3:])

for line in clean_splitted:
    artists.append(line[line.rfind(':') + 4:line.find(' - ')])

songs = pd.DataFrame({'song_title': track_names,
                      'artist': artists})

songs['track'] = songs['song_title'] + " " + songs['artist']
songs = songs[:songs.shape[0] - 1]

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'agffsfdsf42%^!1323fsdf'
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oath().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oath().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('put_song_names', external= True))

@app.route('/putSongsName')
def put_song_names():

    try:
        token_info = get_token()
    except:
        print('user not logged in')
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']

    mnemonic_playlist_id = None

    current_playlist = sp.user_playlists('spotify')['items']
    for playlist in current_playlist:
        if (playlist['name'] == f"Mnemonic {now_day}"):
            return "playlist is alredy created"



    if not mnemonic_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, f'Mnemonic {now_day}', True)
        mnemonic_playlist_id = new_playlist['id']
        song_uris = []
        for song in songs['track']:
            song_uri = sp.search(song, type='track')['tracks']['items'][0]['uri']
            song_uris.append(song_uri)
        sp.user_playlist_add_tracks(user_id, mnemonic_playlist_id, song_uris, None)
        mnemonic_playlist_id = None
        return "playlist successfuly created"





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
    return SpotifyOAuth(client_id = "INSERT_CLIENT_ID",
                        client_secret = "INSERT_CLIENT_SECRET",
                        redirect_uri = url_for('redirect_page', _external= True),
                        scope = 'playlist-read-private user-library-read, playlist-modify-public, playlist-modify-private')

app.run(debug=True)

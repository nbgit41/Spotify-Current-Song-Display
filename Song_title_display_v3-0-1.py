import time, logging, spotipy, json, os
from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import HTTPError
from flask import Flask, render_template_string, jsonify

config_file = "Song_Title_Config.json"

if os.path.exists(config_file):
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print("Error reading config.json, using default settings.", e)
        config = {}
else:
    config = {}

deb = config.get("deb", True)
config_check_interval = config.get("time_between_checks_in_seconds", 0.5)
port_poggies = config.get("port", 5000)
run_on_lan = config.get("accessible_by_other_computers_on_local_network", False)

app = Flask(__name__)

# app.config["TEMPLATES_AUTO_RELOAD"] = True # this is the thing that makes it so that I don't have to reload the entire python file for a html change
if not deb:
    logging.getLogger('werkzeug').setLevel(logging.ERROR) # keeps it from putting extra stuff into the console if debugging is off

creds_location = config.get("spotify_api_info_txt_file", "spotify_secret.txt")
def load_spotify_credentials(filename=creds_location):
    with open(filename, 'r') as file:
        lines = file.readlines()
        client_id = lines[0].strip()  # First line for Client ID
        client_secret = lines[1].strip()  # Second line for Client Secret
    return client_id, client_secret

# Load Spotify credentials from the text file
CLIENT_ID, CLIENT_SECRET = load_spotify_credentials()
REDIRECT_URI = config.get("redirect_URI", 'http://localhost:8888/callback')
SCOPE = 'user-read-currently-playing user-read-playback-state'

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE))

current_song_info = {
    'title': None,
    'artists': None,
    'album_art': None
}

def get_current_song(sp):
    retries = 5
    for i in range(retries):
        try:
            current_track = sp.current_playback()
            if current_track and current_track['is_playing']:
                title = current_track['item']['name']
                artists = ", ".join(artist['name'] for artist in current_track['item']['artists'])  # Combine all artists
                album_art = current_track['item']['album']['images'][0]['url']  # Get the URL of the album art
                return title, artists, album_art
            else:
                return None, None, None
        except HTTPError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                wait_time = 2 ** i  # Exponential backoff
                print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                time.sleep(wait_time)
            else:
                print(f"An error occurred: {e}")
                break
    return None, None, None

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Album Art</title>
          <style>
              :root {
                  --text-alignment: center;
                  
                  --title-font-size: clamp(2rem, 5vw, 4rem);
                  --author-font-size: clamp(1.2rem, 3vw, 2.5rem);
      
                  --main-background-color: #292929;
      
                  --gap-between-art-and-text: 15px;
      
                  --text-color: white;
                  
                  --text-shadow: black 2px 2px 0;
                  --text-stroke-color: black !important;
                  --text-stroke-width: 1px;
                  
                  --album-art-to-left: translatex(-6px); /* IDK why its doing this but this is the best solution I could come up with, this may change depending on the size of the window, I'm not entirely sure. */
              }
              body {
                  text-align: var(--text-alignment);
                  margin: 0 auto;
                  background-color: var(--main-background-color);
                  overflow: hidden;
                  display: flex;
                  align-items: center;
                  column-gap: var(--gap-between-art-and-text);
                  max-height:99vh;
                  max-width:99vw;
              }
              #text {
                  margin: auto;
              }
              h1, h2 {
                  color: var(--text-color);
                  text-shadow: var(--text-shadow);
                  -webkit-text-stroke-color: var(--text-stroke-color);
                  -webkit-text-stroke: var(--text-stroke-width);
                  margin: 0 auto;
              }
              h1 {
                  font-family: SpotifyMixMedium, Arial;
                  font-size: var(--title-font-size);
              }
              h2 {
                  font-family: SpotifyMixLight, Arial;
                  font-size: var(--author-font-size);
              }
              #album-art {
                  max-width: 100vw; /* Increase max width for larger image */
                  max-height: 100vh; /* Maintain aspect ratio */
                  display: block;
                  padding: 0;
                  transform: translatex(-6px);
              }
              @font-face {
                  font-family: 'SpotifyMixMedium';
                  src: local('Spotify Mix Medium'), local('Spotify-Mix-Medium'),
                      url('SpotifyMix-Medium.woff2') format('woff2'),
                      url('SpotifyMix-Medium.woff') format('woff'),
                      url('SpotifyMix-Medium.ttf') format('truetype');
                  font-weight: 500;
                  font-style: normal;
              }
              @font-face {
                  font-family: 'SpotifyMixLight';
                  src: local('Spotify Mix Light'), local('Spotify-Mix-Light'),
                      url('SpotifyMix-Light.woff2') format('woff2'),
                      url('SpotifyMix-Light.woff') format('woff'),
                      url('SpotifyMix-Light.ttf') format('truetype');
                  font-weight: 300;
                  font-style: normal;
              }
          </style>
          </head>
          <body>
            <img id="album-art" src="" alt="Could Not Get Album Art">
            <div id="text">
                <h1 id="title"></h1>
                <h2 id="artists"></h2>
            </div>
            <script>
                // Function to fetch album art when song changes
                function fetchAlbumArt() {
                    fetch('/album-art')
                        .then(response => response.json())
                        .then(data => {
                            if (data.album_art) {
                                document.getElementById('album-art').src = data.album_art;
                            }
                            if (data.title) {
                                document.getElementById('title').innerText = data.title;
                            }
                            if (data.artists) {
                                document.getElementById('artists').innerText = data.artists
                            }
                        });
                }
                // Set an interval to check for updates every 1 seconds, any faster seems rediculus and kinda breaks it especially since it is getting an image.
                setInterval(fetchAlbumArt, 1000);
            </script>
          </body>
        </html>
    ''')

@app.route('/album-art')
def album_art():
    return jsonify({'album_art': current_song_info['album_art'], 'title': current_song_info['title'], 'artists': current_song_info['artists']})

check_number = 1
def update_song_info():
    global check_number
    previous_title = None
    previous_artist = None
    check_interval = config_check_interval
    while True:
        if deb:
            print(f'updating song info {check_number}')
            check_number += 1

        title, artists, album_art = get_current_song(sp)

        # If we have a new song, update the information
        if title and artists:
            if title != previous_title or artists != previous_artist:
                print(f"Now playing: '{title}' by {artists}")

                current_song_info['title'] = title
                current_song_info['artists'] = artists
                current_song_info['album_art'] = album_art  # Update album art only when the song changes

                previous_title = title
                previous_artist = artists
        else:
            print("No song is currently playing.")
            current_song_info['album_art'] = None  # Clear album art if no song is playing

        time.sleep(check_interval)  # Wait for the current check interval

if __name__ == "__main__":
    # Start the song information updater in a separate thread
    import threading
    updater_thread = threading.Thread(target=update_song_info)
    updater_thread.start()

    # Start the Flask app
    if run_on_lan:
        app.run(host="0.0.0.0", port=port_poggies, debug=True)
    else:
        app.run(port=port_poggies, debug=True)

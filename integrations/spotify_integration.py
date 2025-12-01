import spotipy as spo
from spotipy.oauth2 import SpotifyOAuth


scope = "user-library-read"


sp = spo.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']


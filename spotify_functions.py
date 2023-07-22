import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv
load_dotenv() # fetch Spotify API key


# request permissions from Spotify [only has to be defined once]
scope= ['user-library-read', # access "Your Music" library - playlists, liked albums, etc.
        'user-read-playback-state', # view current song & other state-related info. 
        'user-modify-playback-state'] # pause, skip, play, etc.

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(), 
    auth_manager=SpotifyOAuth(scope=scope)
)

devices = sp.devices()
device_id = devices['devices'][0]['id']
print(devices)


### create functions to be used as tools by our agent ###


def find_track_by_name(name):
    results = sp.search(q=name, type='track')
    if (results):
        track_uri = results['tracks']['items'][0]['uri']
        return track_uri


def find_track_by_lyrics(lyrics):
    results = sp.search(q=f"lyrics:{lyrics}", type='track')
    if (results):
        if len(results['tracks']['items']) > 0:
            track_uri = results['tracks']['items'][0]['uri']
            return track_uri
        else:
            return "Couldn't find ya track playa."


def play_track_by_name(track_name): # can also include artist for less popular tracks
    track_uri = find_track_by_name(track_name)
    actual_track_name = sp.track(track_uri)["name"]
    artist_name = sp.track(track_uri)['artists'][0]['name']
    try:
        if (track_uri):
            sp.start_playback(uris=[track_uri])
            #return actual_track_name
            return f"Started playing track {actual_track_name} by {artist_name}." 
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. Don't forget to wake it up!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."


def play_track_by_lyrics(lyrics: str):
    track_uri = find_track_by_lyrics(lyrics)
    actual_track_name = sp.track(track_uri)["name"]
    artist_name = sp.track(track_uri)['artists'][0]['name']
    try:
        if (track_uri):
            sp.start_playback(uris=[track_uri])
            return f"Started playing track {actual_track_name} by {artist_name}." 
        else:
            return "Couldn't find ya track playa."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. Don't forget to wake it up!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."
    

def add_track_to_queue_by_name(track_name):
    track_uri = find_track_by_name(track_name)
    if (track_uri):
        sp.add_to_queue(track_uri)
        return "Successfully added track. to queue."
    else:
        return "Couldn't find ya track playa."


def pause_track():
    try:
        sp.pause_playback()
        return "Playback paused."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. Don't forget to wake it up!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."


def play_track():
    try:
        sp.start_playback()
        return "Playback started."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. Don't forget to wake it up!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."
    

def next_track():
    try:
        sp.next_track()
        return "Successfully skipped to the next track."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. Don't forget to wake it up!"
    except Exception as e: # last resort catch-all
        return f"An unexpected error occurred: {e}."
    

def previous_track():
    try:
        sp.previous_track()
        return "Successfully went back to the previous track."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. Don't forget to wake it up!"
    except Exception as e: # last resort catch-all
        return f"An unexpected error occurred: {e}."
    

#print(play_track_by_lyrics("uzi i am proud of u"))
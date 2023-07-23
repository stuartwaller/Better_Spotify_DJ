import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException
import random
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
#print(devices)


### create functions to be used as tools by our agent ##

def find_track_by_name(name):
    results = sp.search(q=name, type='track')
    track_uri = results['tracks']['items'][0]['uri']
    return track_uri


def find_track_by_lyrics(lyrics):
    results = sp.search(q=f"lyrics:{lyrics}", type='track')
    if len(results['tracks']['items']) > 0:
        track_uri = results['tracks']['items'][0]['uri']
        return track_uri


def play_track_by_name(track_name): # can also include artist for less popular tracks
    track_uri = find_track_by_name(track_name)
    actual_track_name = sp.track(track_uri)["name"]
    artist_name = sp.track(track_uri)['artists'][0]['name']
    try:
        if (track_uri):
            sp.start_playback(uris=[track_uri])
            return f"Now playing {actual_track_name} by {artist_name}." 
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\n Remember to wake up Spotify!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."


def play_track_by_lyrics(lyrics: str):
    track_uri = find_track_by_lyrics(lyrics)
    actual_track_name = sp.track(track_uri)["name"]
    artist_name = sp.track(track_uri)['artists'][0]['name']
    try:
        if (track_uri):
            sp.start_playback(uris=[track_uri])
            return f"Now playing {actual_track_name} by {artist_name}." 
        else:
            return "Couldn't find ya track playa."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\nRemember to wake up Spotify!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."
    

def add_track_to_queue_by_name(track_name):
    track_uri = find_track_by_name(track_name)
    sp.add_to_queue(track_uri)
    return "Successfully added track. to queue."
  

def pause_track():
    sp.pause_playback()
    return "Playback paused."


def play_track():
    sp.start_playback()
    return "Playback started."


def next_track():
    sp.next_track()
    return "Successfully skipped to the next track."


def previous_track():
    try:
        sp.previous_track()
        return "Successfully went back to the previous track."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\nPerhaps there was no previous track!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."


# employing string similarity search as prior method was case sensitive
# for example, "play certified bangers" wouldn't yield anything
import Levenshtein as lev
def play_my_playlist(playlist_name): 
    results = sp.current_user_playlists()

    # Calculate the Levenshtein distance from the input to each playlist name, and pick the closest
    closest_playlist = None
    closest_distance = None
    for item in results['items']:
        distance = lev.distance(playlist_name.lower(), item['name'].lower())
        if closest_distance is None or distance < closest_distance:
            closest_playlist = item
            closest_distance = distance
    if not closest_playlist:
        raise Exception(f"No playlists found.")
    
    playlist_uri = closest_playlist['uri']
    sp.start_playback(context_uri=playlist_uri)
    return f"Now bumping {closest_playlist['name']} by {closest_playlist['owner']['display_name']}"


def track_name_and_artist(track_info): 
    track_name = track_info['tracks'][0]['name']
    artist = track_info['tracks'][0]['artists'][0]['name']
    return f"Started playing {track_name} by {artist}."


def get_my_track_recommendations():
    results = sp.current_user_top_tracks(limit=5)
    top_track_ids = [track['id'] for track in results['items']]
    recommendations = sp.recommendations(seed_tracks=top_track_ids, limit=5)
    recommended_track_uris = [track['uri'] for track in recommendations['tracks']]
    sp.start_playback(uris=[recommended_track_uris[0]])
    for uri in recommended_track_uris[1:]:
        sp.add_to_queue(uri)
    return track_name_and_artist(recommendations)


def play_similar_track(track_name): 
    print("Bet, let me think of something similar.")
    track_uri = find_track_by_name(track_name)
    recommendations = sp.recommendations(seed_tracks=[track_uri], limit=1)
    recommended_track_uris = [track['uri'] for track in recommendations['tracks']]
    sp.start_playback(uris=[recommended_track_uris[0]])
    return f"How about this: {track_name_and_artist(recommendations)}."

### ### ### ### ### SEXY FUNCTIONS BELOW ### ### ### ### ###

def get_all_tracks(artist):
    results = sp.search(q='artist:' + artist, type='artist')
    try: 
        artist_id = results['artists']['items'][0]["id"]
    except IndexError:
        raise Exception(f"Could not find {artist}. Please check spelling.")
    top_tracks = sp.artist_top_tracks(artist_id)['tracks']
    albums = sp.artist_albums(artist_id, album_type='album')
    all_tracks = []
    for album in albums['items']:
        album_tracks = sp.album_tracks(album['id'])['items']
        all_tracks.extend(album_tracks)
    random.shuffle(all_tracks)
    all_tracks = top_tracks + all_tracks
    return all_tracks
    

import random
def get_chill_tracks(artist): 
    all_tracks = get_all_tracks(artist)
    chill_tracks = []
    for track in all_tracks:
        features = sp.audio_features(track['id'])[0]
        if features['tempo'] < 120 and features['energy'] < 0.65: # arbitrary "chill" metrics
            chill_tracks.append(track)
        if len(chill_tracks) == 10:
            break
    random.shuffle(chill_tracks) # shuffles in place; nothing returned
    # note: gpt4 amazing for debugging
    return chill_tracks


def get_hype_tracks(artist): 
    all_tracks = get_all_tracks(artist)
    hype_tracks = []
    for track in all_tracks:
        features = sp.audio_features(track['id'])[0]
        if features['tempo'] > 120 and features['energy'] > 0.65: # arbitrary "hype" metrics
            hype_tracks.append(track)
        if len(hype_tracks) == 10:
            break
    random.shuffle(hype_tracks)
    return hype_tracks


def get_dance_tracks(artist): 
    all_tracks = get_all_tracks(artist)
    dance_tracks = []
    for track in all_tracks:
        features = sp.audio_features(track['id'])[0]
        if features['danceability'] > 0.85: # arbitrary "dance" metrics
            dance_tracks.append(track)
        if len(dance_tracks) == 10:
            break
    random.shuffle(dance_tracks)
    return dance_tracks


from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage  

llm = ChatOpenAI(max_retries=3, temperature=0, model_name = "gpt-3.5-turbo-0613")

def play_some_tracks(artist): 
    if artist.lower() == "drake":
        print("MR OCTOBER, good choice. Love me some Drizzy.") # easteregg eheh

    vibe = input("What vibe are you feeling? ")
    messages = [
    SystemMessage(
        content="""Based off the user's input, classify them as one of
        'chill', 'hype', or 'dance'. Only return their classification."""
    ),
    HumanMessage(
        content=vibe
    ),
    ]
    ai_response = str(llm(messages))
    print(ai_response)

    print(f"Great, please wait while I queue up some {artist.title()}.")
    
    if "chill" in ai_response:
        tracks = get_chill_tracks(artist)
    if "hype" in ai_response: 
        tracks = get_hype_tracks(artist)
    if "dance" in ai_response: 
        tracks = get_dance_tracks(artist)

    sp.start_playback(uris=[tracks[0]['uri']])
    for track in tracks[1:]:
        sp.add_to_queue(uri=track['uri'])
    return f"Here are 10 {artist.title()} tracks to match your vibe. Enjoy."


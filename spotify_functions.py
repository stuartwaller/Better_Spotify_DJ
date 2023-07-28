import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException
import random
from dotenv import load_dotenv
load_dotenv() 


scope= ['user-library-read', 
        'user-read-playback-state', 
        'user-modify-playback-state'] 

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(), 
    auth_manager=SpotifyOAuth(scope=scope)
)

devices = sp.devices()
device_id = devices['devices'][0]['id']
#print(devices)


### ### create functions to be used as tools by our agent ### ###

def find_track_by_name(name):
    results = sp.search(q=name, type='track')
    track_uri = results['tracks']['items'][0]['uri']
    return track_uri


def find_track_by_lyrics(lyrics):
    results = sp.search(q=f"lyrics:{lyrics}", type='track')
    if len(results['tracks']['items']) > 0:
        track_uri = results['tracks']['items'][0]['uri']
        return track_uri


# IMPORTANT for less-popular tracks, "play {track} {artist}"
def play_track_by_name(track_name): # can also include artist to find less popular tracks
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
    return "Successfully added track to the queue."
  

def pause_track():
    sp.pause_playback()
    return "Playback paused."


def play_track():
    sp.start_playback()
    return "Playback started."


def skip_track():
    sp.next_track()
    return "Successfully skipped to the next track."


def skip_all_tracks():
    while True:
        # Get details of currently playing track
        current_track = sp.current_playback()
        
        # If no track is currently playing
        if not current_track:
            return "No track currently playing."

        # Skip to the next track
        sp.next_track()

        # Get details of the new track
        new_track = sp.current_playback()
        
        # If no new track started playing after skip, it indicates end of queue
        if not new_track or new_track['item']['id'] == current_track['item']['id']:
            return "End of queue reached or no more tracks to skip."
 

def previous_track():
    try:
        sp.previous_track()
        return "Successfully went back to the previous track."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\nPerhaps there was no previous track!"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."
    

def play_album(album: str, artist: str):
    # search for the album
    results = sp.search(q=f'album:{album} artist:{artist}', type='album')

    # check if the album was found
    if results['albums']['items']:
        album_id = results['albums']['items'][0]['id']

        # get a list of track URIs for the album
        tracks = sp.album_tracks(album_id)
        track_uris = [track['uri'] for track in tracks['items']]

        # start playing the album
        sp.start_playback(uris=track_uris)
        return f"Started playing {album} by {artist}."
    else:
        return f"Album '{album}' by '{artist}' not found."


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
    recommended_track_uris = [track['uri'] for track in recommendations['tracks']] # list of uris
    sp.start_playback(uris=[uri for uri in recommended_track_uris])

    track_name_and_artist_list = []
    for uri in recommended_track_uris:
        track = sp.track(uri)
        track_artists = ', '.join([artist['name'] for artist in track['artists']])
        track_name_and_artist_list.append(f"{track['name']} --- {track_artists}\n")

    return f"Here are my recommendations for you:\n\n {', '.join(track_name_and_artist_list)}"


def play_similar_track(track_name): # recommending similar track based on current track
    track_uri = find_track_by_name(track_name)
    recommendations = sp.recommendations(seed_tracks=[track_uri], limit=1)
    recommended_track_uris = [track['uri'] for track in recommendations['tracks']]
    sp.start_playback(uris=[recommended_track_uris[0]])
    return f"How about this: {track_name_and_artist(recommendations)}."


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


track_limit = 10


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


def get_popular_tracks(artist):
    results = sp.search(q='artist:' + artist, type='artist')
    try: 
        artist_id = results['artists']['items'][0]["id"]
    except IndexError:
        raise Exception(f"Could not find {artist}. Please check spelling.")
    top_tracks = sp.artist_top_tracks(artist_id)['tracks']
    return top_tracks


# get chill, hype, and dance functions could be optimized a bit


import random
def get_chill_tracks(artist): 
    all_tracks = get_all_tracks(artist)
    chill_tracks = []
    for track in all_tracks:
        features = sp.audio_features(track['id'])[0]
        if features['tempo'] < 120 and features['energy'] < 0.65: # arbitrary "chill" metrics
            chill_tracks.append(track)
        if len(chill_tracks) == track_limit:
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
        if len(hype_tracks) == track_limit:
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
        if len(dance_tracks) == track_limit:
            break
    random.shuffle(dance_tracks)
    return dance_tracks


from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage  
from audio import play_generated_audio # for audio
from dotenv import load_dotenv
load_dotenv()  


llm = ChatOpenAI(max_retries=3, temperature=0, model_name = "gpt-4")


def play_artist_tracks(artist: str, vibe: str): 

    try_again_msg = """
    For a more personalized experience, please tell me your current vibe/mood.
    """

    messages = [
    SystemMessage(
        content="""
        Based off the user's input, classify them as one of
        'chill', 'hype', 'dance', 'popular,' or 'nothing'. Only return their classification.

        If the user only mentioned an artist's name, they are 'nothing'.
        """
    ),
    HumanMessage(
        content=vibe
    ),
    ]
    ai_response = str(llm(messages))
    print(ai_response) # debugging purposes

    if "nothing" in ai_response: 
        return try_again_msg
    if "popular" in ai_response:
        tracks = get_popular_tracks(artist)
    if "chill" in ai_response:
        tracks = get_chill_tracks(artist)
    if "hype" in ai_response: 
        tracks = get_hype_tracks(artist)
    if "dance" in ai_response: 
        tracks = get_dance_tracks(artist)

    sp.start_playback(uris=[track['uri'] for track in tracks])
    #for track in tracks[1:]:
        #sp.add_to_queue(uri=track['uri'])
        
    if artist.lower() == "drake":
        drake_message = "LOVE ME SOME DRIZZY. GREAT CHOICE."
        return drake_message + f"\nHere are the {len(tracks)} {artist.title()} tracks for you."
    else:
        return f"\nHere are the {len(tracks)} {artist.title()} tracks for you."


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


import lyricsgenius
import requests
from bs4 import BeautifulSoup


def get_all_track_info(): 
    current_track = sp.current_user_playing_track()
    track_name = current_track['item']['name']
    artist = current_track['item']['artists'][0]['name']

    basic_info = { # basic info
        'name': track_name,
        'artist': artist,
        'album': current_track['item']['album']['name'],
        'release_date': current_track['item']['album']['release_date'],
    }
    basic_info = "\n\n---BASIC INFO---\n\n" + str(basic_info)

    # features hinder the search results
    if " (with " in track_name:
        track_name = track_name.split(" (with ")[0]
    elif " (feat. " in track_name:
        track_name = track_name.split(" (feat. ")[0]

    genius = lyricsgenius.Genius()
    track = genius.search_song(track_name, artist)
    if track:
        lyrics = "\n\n---LYRICS---\n\n" + track.lyrics 
    else:
        print(f"Unable to find lyrics for {track_name} by {artist}.")

    # fetching more information
    url = track.url
    response = requests.get(url)
    # parsing the webpage 
    soup = BeautifulSoup(response.text, 'html.parser')
    # locating the 'ABOUT' section
    more_info = soup.select_one('div[class^="RichText__Container-oz284w-0"]')
    track_info = basic_info + lyrics

    if more_info:
        more_info = "\n\n---MORE INFO---\n\n" +more_info.get_text(separator='\n')
        track_info = basic_info + lyrics + more_info # big string
        
    else:
        print(f"Unable to find 'ABOUT' for {track_name} by {artist}.")

    return track_info


import codecs


def summarize_track_info(): 
    track_info = get_all_track_info()
    messages = [
    SystemMessage(
        content=
        """ 
        The song information you will be given is divided into three parts: 

	    1) 'BASIC INFO' Basic information about the song. 
	    2) 'LYRICS' The song lyrics. 
	    3) 'MORE INFO' More information about the song, artist, and or context of the work. 
	
        In the first sentence - a single sentence - state the basic information.

        *skip a line* 

        Then, in 5-7 sentences, using the remaining two sections, interpret the essence of the song. 
        Make sure to include all the details in the 'MORE INFO' section, 
        but derive most of your song-meaning interpretation from the 'LYRICS', which will comprise
        the bulk of your write-up. Make your summary captivating and sophisticated.
        """
    ),
    HumanMessage(
        content=track_info
    ),
    ]
    ai_response = str(llm(messages))
    # cleaning
    ai_response = ai_response.replace('content=', '').replace('additional_kwargs={}', '').replace('example=False', '')
    ai_response = codecs.decode(ai_response, 'unicode_escape')
    return ai_response








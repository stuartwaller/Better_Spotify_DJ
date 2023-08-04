import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage  
import re
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
load_dotenv() 


llm = ChatOpenAI(max_retries=3, temperature=0, model_name = "gpt-4")


### ### ### Spotify Setup ### ### ###


scope= ['user-library-read', 
        'user-read-playback-state', 
        'user-modify-playback-state'] 


sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(), 
    auth_manager=SpotifyOAuth(scope=scope)
)


devices = sp.devices()
device_id = devices['devices'][0]['id']


### ### ### Basic Functions ### ### ###


def find_track_by_name(track_name):
    """
    Searches track by name to get uri
    """
    results = sp.search(q=track_name, type='track')
    track_uri = results['tracks']['items'][0]['uri']
    return track_uri


def play_track_by_name(track_name): 
    """
    Plays track given its name
    For less popular tracks, do 'play {track} {artist}'
    """
    track_uri = find_track_by_name(track_name)
    track_name = sp.track(track_uri)["name"]
    artist_name = sp.track(track_uri)['artists'][0]['name']
    try:
        sp.start_playback(device_id=device_id, uris=[track_uri])
        return f"Now playing {track_name} by {artist_name}."
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\n**Remember to wake up Spotify.**"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."


def queue_track_by_name(track_name):
    """
    Queues track given its name
    """
    track_uri = find_track_by_name(track_name)
    track_name = sp.track(track_uri)["name"]
    sp.add_to_queue(uri=track_uri, device_id=device_id)
    return f"Added {track_name} to your queue."
  

def pause_track():
    sp.pause_playback(device_id=device_id)
    return "Playback paused."


def play_track():
    sp.start_playback(device_id=device_id)
    return "Playback started."


def skip_track():
    sp.next_track(device_id=device_id)
    return "Skipped to your next track."
 
    
### ### ### More Elaborate ### ### ###
    

def play_album_by_name_and_artist(album_name, artist_name):
    """
    Plays an album given its name and artist
    context_uri (for artist, album, or playlist) expects a string
    """
    results = sp.search(q=f'{album_name} {artist_name}', type='album')
    album_id = results['albums']['items'][0]['id']
    album_info = sp.album(album_id)
    album_name = album_info['name']
    artist_name = album_info['artists'][0]['name']
    try: 
        sp.start_playback(device_id=device_id, context_uri=f'spotify:album:{album_id}')
        return f"Now playing {album_name} by {artist_name}."
    except spotipy.SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\n**Remember to wake up Spotify.**"
    except Exception as e: 
        return f"An unexpected error occurred: {e}."


def play_playlist_by_name(playlist_name):
    """
    This function takes a user-provided playlist name as input and plays 
    the name of the real, matching playlist from the user's existing playlists on Spotify.
    """
    playlists = sp.current_user_playlists()
    playlist_dict = {playlist['name']: (playlist['id'], playlist['owner']['display_name']) for playlist in playlists['items']}
    
    system_message_content = """
        The task is to find a match between the user-requested playlist name and
        the user's existing playlists. Only return the name of the match.
        """
    human_message_content = f"""
        User's requested playlist: {playlist_name}
        User's existing playlists: {list(playlist_dict.keys())}
        """
    messages = [
        SystemMessage(content=system_message_content),
        HumanMessage(content=human_message_content)
    ]

    ai_response = str(llm(messages))
    playlist_name = re.search("'(.*)'", ai_response).group(1)
    try: 
        playlist_id, creator_name = playlist_dict[playlist_name]
        sp.start_playback(device_id=device_id, context_uri=f'spotify:playlist:{playlist_id}')
        return f'Now playing {playlist_name} by {creator_name}.'
    except: 
        return "Unable to find playlist. Please try again."
  

# avoid creating new object everytime function is called
genius = lyricsgenius.Genius() 
def get_track_info(): 
    """
    Harvests information for explain_track() using the Genius API and webscraping. 
    """
    current_track_item = sp.current_user_playing_track()['item']
    track_name = current_track_item['name']
    artist_name = current_track_item['artists'][0]['name']
    album_name = current_track_item['album']['name']
    release_date = current_track_item['album']['release_date']
    basic_info = {
        'track_name': track_name,
        'artist_name': artist_name,
        'album_name': album_name,
        'release_date': release_date,
    }
    # features hinder Genius search
    track_name = re.split(' \(with | \(feat\. ', track_name)[0]
    result = genius.search_song(track_name, artist_name)
    lyrics = result.lyrics
    url = result.url
    response = requests.get(url)
    # parsing the webpage 
    soup = BeautifulSoup(response.text, 'html.parser')
    # locating the 'ABOUT' section
    about_section = soup.select_one('div[class^="RichText__Container-oz284w-0"]')
    about_section = about_section.get_text(separator='\n')
    return basic_info, about_section, lyrics, url


def explain_track(): 
    """
    Presents track information in an organized, compelling manner. 
    """
    basic_info, about_section, lyrics, url = get_track_info()
    system_message_content = """
        Your task is to create an engaging summary for a track using the available details
        about the track and its lyrics. If there's insufficient or no additional information
        besides the lyrics, craft the entire summary based solely on the lyrical content."
        """
    human_message_content = f"{about_section}\n\n{lyrics}"
    messages = [
        SystemMessage(content=system_message_content),
        HumanMessage(content=human_message_content)
    ]
    ai_response = str(llm(messages))
    ai_response = ai_response.split("content='")[1].split(" additional_kwargs")[0]
    summary = f"""
        **Name:** {basic_info["track_name"]}   
        **Artist:** {basic_info["artist_name"]}   
        **Album:** {basic_info["album_name"]}   
        **Release:** {basic_info["release_date"]}   

        **About:** 
        {ai_response}

        **More:**  
        {url}
    """
    return summary


### ### ### Personalization ### ### ###


def get_user_mood(user_mood): 
    """
    """
    system_message_content = """
        Your task is to evaluate the user's response to the question
        'How are you feeling today' and determine their emotional state. 
        Categorize this state into one of the four predefined moods: happy, sad, energetic, or calm. 
        Remember, always return only the mood category as your output.
        """
    human_message_content = user_mood
    messages = [
        SystemMessage(content=system_message_content),
        HumanMessage(content=human_message_content)
    ]
    ai_response = llm(messages).content
    user_mood = ai_response
    return user_mood


model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
genre_list = sp.recommendation_genre_seeds()["genres"]
genre_embeddings = model.encode(genre_list)


def get_genre_by_name(genre_name): 
    """
    """
    if genre_name.lower() in genre_list:
        genre_name = genre_name.lower()
        return genre_name
    else:
        genre_name_embedding = model.encode([genre_name.lower()])
        similarity_scores = cosine_similarity(genre_name_embedding, genre_embeddings)
        most_similar_index = similarity_scores.argmax()
        genre_name = genre_list[most_similar_index]
        return genre_name


mood_settings = {
    "happy": {"max_instrumentalness": 0.001, "min_valence": 0.5},
    "sad": {"max_danceability": 0.75, "max_valence": 0.5},
    "energetic": {"min_tempo": 120, "min_danceability": 0.65},
    "calm": {"max_energy": 0.75, "max_tempo": 140}
}


seed_artist_limit = 1
track_limit = 5
def play_genre_by_name_and_mood(genre_name, user_mood):
    """
    """
    genre_name = get_genre_by_name(genre_name)
    print(genre_name) # debugging
    user_mood = get_user_mood(user_mood)
    print(user_mood) # debugging
    mood_setting = mood_settings[user_mood]
    # increased personalization
    #user_top_artists = sp.current_user_top_artists(limit=seed_artist_limit, time_range="medium_term")
    #user_top_artists_ids = [artist['id'] for artist in user_top_artists['items']]

    recommendations = sp.recommendations( # can pass maximum {genre + artists} = 5 seeds
                                    seed_artists=None, 
                                    seed_genres=[genre_name], 
                                    seed_tracks=None, 
                                    limit=track_limit, # 20 default
                                    country=None,
                                    **mood_setting
                                    )
    track_uris = [track['uri'] for track in recommendations['tracks']]
    sp.start_playback(device_id=device_id, uris=track_uris)
    return f"Now playing {genre_name}."





















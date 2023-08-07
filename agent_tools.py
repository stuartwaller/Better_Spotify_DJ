from pydantic import BaseModel, Field
from langchain.agents import tool 
import spotify_functions as spf


class TrackNameInput(BaseModel):
    track_name: str = Field(description="Track name in the user's request.")  


class AlbumNameAndArtistNameInput(BaseModel):
    album_name: str = Field(description="Album name in the user's request.")
    artist_name: str = Field(description="Artist name in the user's request.") 


class PlaylistNameInput(BaseModel):
    playlist_name: str = Field(description="Playlist name in the user's request.") 


class GenreNameAndUserMoodInput(BaseModel):
    genre_name: str = Field(description="Genre name in the user's request.")
    user_mood: str = Field(description="User's current mood/state-of-being.") 


class ArtistNameAndUserMoodInput(BaseModel):
    artist_name: str = Field(description="Artist name in the user's request.") 
    user_mood: str = Field(description="User's current mood/state-of-being.") 

# return_direct=True returns tool output directly to user
@tool("play_track_by_name", return_direct=True, args_schema=TrackNameInput) 
def tool_play_track_by_name(track_name: str) -> str:
    """
    Use this tool when a user wants to play a particular track by its name. 
    You will need to identify the track name from the user's request. 
    Usually, the requests will look like 'play {track name}'. 
    This tool is specifically designed for clear and accurate track requests.
    """
    return spf.play_track_by_name(track_name)


@tool("queue_track_by_name", return_direct=True, args_schema=TrackNameInput)
def tool_queue_track_by_name(track_name: str) -> str:
    """
    Use this tool when a user wants to queue a track. 
    You will need to identify the track name from the user's request.
    """
    return spf.queue_track_by_name(track_name)


@tool("pause_track", return_direct=True)
def tool_pause_track(query: str) -> str:
    """
    Use this tool when a user wants to pause their music.
    """
    return spf.pause_track()


@tool("play_track", return_direct=True) 
def tool_play_track(query: str) -> str:
    """
    Use this tool when a user wants to play/resume/unpause their music.
    """
    return spf.play_track()


@tool("skip_track", return_direct=True)
def tool_skip_track(query: str) -> str:
    """
    Use this tool when a user wants to skip/go to the next track.
    """
    return spf.skip_track()


@tool("play_album_by_name_and_artist", return_direct=True, args_schema=AlbumNameAndArtistNameInput) 
def tool_play_album_by_name_and_artist(album_name: str, artist_name: str) -> str:
    """
    Use this tool when a user wants to play an album.
    You will need to identify both the album name and artist name from the user's request.
    Usually, the requests will look like 'play the album {album_name} by {artist_name}'. 
    """
    return spf.play_album_by_name_and_artist(album_name, artist_name)


@tool("play_playlist_by_name", return_direct=True, args_schema=PlaylistNameInput) 
def tool_play_playlist_by_name(playlist_name: str) -> str:
    """
    Use this tool when a user wants to play one of their playlists.
    You will need to identify the playlist name from the user's request. 
    """
    return spf.play_playlist_by_name(playlist_name)


@tool("explain_track", return_direct=True) 
def tool_explain_track(query: str) -> str:
    """
    Use this tool when a user wants to know about the current track.
    """
    return spf.explain_track()


@tool("play_genre_by_name_and_mood", return_direct=True, args_schema=GenreNameAndUserMoodInput) 
def tool_play_genre_by_name_and_mood(genre_name: str, user_mood: str) -> str:
    """
    Use this tool when a user wants to play a genre.
    You will need to identify both the genre name from the user's request, 
    and also their current mood, which you should always be monitoring;
    If the user requests a genre without explicitly stating their mood, ask them 
    for their mood first. 
    """
    return spf.play_genre_by_name_and_mood(genre_name, user_mood)


@tool("play_artist_by_name_and_mood", return_direct=True, args_schema=ArtistNameAndUserMoodInput) 
def tool_play_artist_by_name_and_mood(artist_name: str, user_mood: str) -> str:
    """
    Use this tool when a user wants to play an artist.
    You will need to identify both the artist name from the user's request, 
    and also their current mood, which you should always be monitoring;
    If the user requests an artist without explicitly stating their mood, ask them 
    for their mood first. 
    """
    return spf.play_artist_by_name_and_mood(artist_name, user_mood)














# llm will intelligently decide which tool to use from this list
custom_tools =[
    tool_play_track_by_name,
    tool_queue_track_by_name,
    tool_pause_track,
    tool_play_track,
    tool_skip_track,
    tool_play_album_by_name_and_artist,
    tool_play_playlist_by_name,
    tool_explain_track,
    tool_play_genre_by_name_and_mood,
    tool_play_artist_by_name_and_mood
]


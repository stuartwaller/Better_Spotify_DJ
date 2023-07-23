from pydantic import BaseModel, Field
from langchain.tools import tool
import spotify_functions as spf


class TrackNameInput(BaseModel):
    track_name: str = Field(
        description="Track name in the user's request")  


class TrackLyricsInput(BaseModel):
    lyrics: str = Field(
        description="Track lyrics in the user's request")
    

class ArtistNameInput(BaseModel):
    artist: str = Field(
        description="Artist in the user's request")  
    

class PlaylistNameInput(BaseModel):
    playlist_name: str = Field(
        description="Playlist name in the user's request")  
    

@tool("play_similar_track", return_direct=True, args_schema=TrackNameInput) 
def tool_play_similar_track(track_name: str) -> str:
    """Extract the track name from user's request and play a similar track."""
    return spf.play_similar_track(track_name)
    

@tool("play_my_playlist", return_direct=True, args_schema=PlaylistNameInput) 
def tool_play_my_playlist(playlist_name: str) -> str:
    """Extract the playlist name from user's request and play it."""
    return spf.play_my_playlist(playlist_name)
    

@tool("play_some_tracks", return_direct=True, args_schema=ArtistNameInput) 
def tool_play_some_tracks(artist: str) -> str:
    """Extract the artist name from user's request and queue up their songs.
    The user will not mention track names, only the artist's name."""
    return spf.play_some_tracks(artist)


@tool("get_my_track_recommendations", return_direct=True) 
def tool_get_my_track_recommendations(query: str) -> str:
    """Play the user recommendations; tracks they would like."""
    return spf.get_my_track_recommendations()


# return_direct=True returns tool output directly to user
# args_schema because our play_track_by_name function requires an input
# @tool decorator modifies our function
# to find your track, follow this structure exactly: play {song} {artist} | no "by"
# docstrings are mandatory; included in metaprompt for agent telling it what tool is for
@tool("play_track_by_name", return_direct=True, args_schema=TrackNameInput) 
def tool_play_track_by_name(track_name: str) -> str:
    """Extract the track name from user's request and immediately play the track."""
    return spf.play_track_by_name(track_name)


@tool("play_track_by_lyrics", return_direct=True, args_schema=TrackLyricsInput)
def tool_play_track_by_lyrics(lyrics: str) -> str:
    """Extract the track lyrics from user's request and immediately play the track."""
    return spf.play_track_by_lyrics(lyrics)


@tool("add_track_to_queue_by_name", return_direct=True, args_schema=TrackNameInput)
def tool_add_track_to_queue_by_name(track_name: str) -> str:
    """Extract the track name from user's request and add track to queue."""
    return spf.add_track_to_queue_by_name(track_name)


@tool("play_track", return_direct=True) # Problem: agent doesn't respond to just "play"
def tool_play_track(query: str) -> str:
    """Start playing the current track."""
    return spf.play_track()


@tool("pause_track", return_direct=True)
def tool_pause_track(query: str) -> str:
    """Pause the current track."""
    return spf.pause_track()


@tool("next_track", return_direct=True)
def tool_next_track(query: str) -> str:
    """Play next track."""
    return spf.next_track()


@tool("previous_track", return_direct=True)
def tool_previous_track(query: str) -> str:
    """Play previous track."""
    return spf.previous_track()


# llm will intelligently decide which tool to use from this list
custom_tools =[
    tool_play_track_by_name,
    tool_play_track_by_lyrics,
    tool_add_track_to_queue_by_name,
    tool_pause_track,
    tool_play_track,
    tool_next_track,
    tool_previous_track,
    tool_play_some_tracks,
    tool_play_my_playlist,
    tool_get_my_track_recommendations, 
    tool_play_similar_track
]

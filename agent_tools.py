from pydantic import BaseModel, Field
from langchain.agents import tool # was langchain.tools
import spotify_functions as spf


class TrackNameInput(BaseModel):
    track_name: str = Field(
        description="Track name in the user's request")  


class TrackLyricsInput(BaseModel):
    lyrics: str = Field(
        description="Track lyrics in the user's request")
    

class ArtistVibeInput(BaseModel):
    artist: str = Field(description="Artist in the user's request")
    vibe: str = Field(description="Vibe in the user's request")


class AlbumArtistInput(BaseModel):
    album: str = Field(description="Album in the user's request")
    artist: str = Field(description="Artist in the user's request")


class PlaylistNameInput(BaseModel):
    playlist_name: str = Field(
        description="Playlist name in the user's request")  
    

@tool("summarize_track_info", return_direct=True) 
def tool_summarize_track_info(query: str) -> str:
    """When a user wants to know any information about the current track."""
    return spf.summarize_track_info()
    

@tool("play_similar_track", return_direct=True, args_schema=TrackNameInput) 
def tool_play_similar_track(track_name: str) -> str:
    """Extract the track name from user's request and play a similar track."""
    return spf.play_similar_track(track_name)
    

@tool("play_album", return_direct=True, args_schema=AlbumArtistInput) 
def tool_play_album(album: str, artist: str) -> str:
    """Extract the album and artist from user's request and play the album."""
    return spf.play_album(album, artist)


@tool("play_my_playlist", return_direct=True, args_schema=PlaylistNameInput) 
def tool_play_my_playlist(playlist_name: str) -> str:
    """Extract the playlist name from user's request and play it."""
    return spf.play_my_playlist(playlist_name)
    

@tool("play_artist_tracks", return_direct=True, args_schema=ArtistVibeInput) 
def tool_play_artist_tracks(artist: str, vibe: str) -> str:
    """
    Extract the artist name and vibe from user's request and queue up their songs.
    """
    return spf.play_artist_tracks(artist, vibe)


@tool("get_my_track_recommendations", return_direct=True) 
def tool_get_my_track_recommendations(query: str) -> str:
    """Play the user recommendations; tracks they would like."""
    return spf.get_my_track_recommendations()


# return_direct=True returns tool output directly to user
# args_schema because our play_track_by_name function requires an input
# @tool decorator modifies our function
@tool("play_track_by_name", return_direct=True, args_schema=TrackNameInput) 
def tool_play_track_by_name(track_name: str) -> str:
    """
    Extract the track name from user's request and immediately play the track.
    Do not use this tool if the user only enters an artist's name. 
    """
    return spf.play_track_by_name(track_name)


@tool("play_track_by_lyrics", return_direct=True, args_schema=TrackLyricsInput)
def tool_play_track_by_lyrics(lyrics: str) -> str:
    """Extract the track lyrics from user's request and immediately play the track."""
    return spf.play_track_by_lyrics(lyrics)


@tool("add_track_to_queue_by_name", return_direct=True, args_schema=TrackNameInput)
def tool_add_track_to_queue_by_name(track_name: str) -> str:
    """
    Extract the track name from user's request and add track to queue.
    Do not use this tool if the user only enters an artist's name. 
    """
    return spf.add_track_to_queue_by_name(track_name)


@tool("play_track", return_direct=True) # Problem: agent doesn't respond to just "play"
def tool_play_track(query: str) -> str:
    """Start playing the current track."""
    return spf.play_track()


@tool("pause_track", return_direct=True)
def tool_pause_track(query: str) -> str:
    """Pause the current track."""
    return spf.pause_track()


@tool("skip_track", return_direct=True)
def tool_skip_track(query: str) -> str:
    """Play next track."""
    return spf.skip_track()


@tool("skip_all_tracks", return_direct=True)
def tool_skip_all_tracks(query: str) -> str:
    """Skip all tracks in the queue."""
    return spf.skip_all_tracks()


@tool("previous_track", return_direct=True)
def tool_previous_track(query: str) -> str:
    """Play previous track."""
    return spf.previous_track()


# llm will intelligently decide which tool to use from this list
custom_tools =[
    tool_play_track_by_name,
    tool_play_track_by_lyrics,
    tool_play_album,
    tool_add_track_to_queue_by_name,
    tool_pause_track,
    tool_play_track,
    tool_skip_track,
    tool_skip_all_tracks,
    tool_previous_track,
    tool_play_artist_tracks,
    tool_play_my_playlist,
    tool_get_my_track_recommendations, 
    tool_play_similar_track,
    tool_summarize_track_info
]



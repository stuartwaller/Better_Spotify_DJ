from main import agent_executor
import gradio as gr


description = """
<div align='center'>
    <img src='file/icon.jpeg' style='opacity: 0.5;'/>
    <br/>
    <p style="font-size: 15px;">Press any key to begin.</p>
    <strong style="font-size: 20px;">For a more personalized experience, tell me your mood, or what you're doing.</strong><br>
    <code style="font-size: 15px;">{}</code> indicates a specific name.<br><br>
</div>
"""


examples = ["Play Passionfruit", 
            "Explain this song", 
            "Passionfruit is my favorite song and I like Rihanna, recommend me songs", 
            "Create me a playlist based on my love for jazz and the song Blinding Lights"
]


instructions = """
<h3 style="color: #4A90E2;">🌟 Basic Commands 🌟</h3>

<ul>
    <li>🎵 <strong>Specific Song:</strong> <code>Play {song}</code> 
    <ul>
        <li> Include <code>{artist}</code> if less popular</li>
    </ul>
    <li>⏭️ <strong>Controls:</strong> Use <code>Queue</code>, <code>Pause</code>, <code>Resume</code>, or <code>Skip</code></li>
    <li>ℹ️ <strong>Song Info:</strong> <code>Explain this song</code></li>
    <li>📀 <strong>Album:</strong> <code>Play {album} album</code> 
    <ul>
        <li> Include <code>{artist}</code> if less popular</li>
    </ul>
    <li>🎶 <strong>Playlist:</strong> <code>Play {playlist} playlist</code></li>
</ul>
<br>
<h3 style="color: #4A90E2;">🌟 Personalized Commands 🌟</h3>

<ul>
    <li>🎧 <strong>Genre:</strong> <code>Play {genre}</code></li>
    <li>🎤 <strong>Artist:</strong> <code>Play {artist}</code></li>
    <li>🌐 <strong>Recommendations:</strong> <code>Play recommendations</code></li>
    <ul>
        <li><code>Passionfruit is my favorite song and I like Rihanna, recommend me songs</code></li>
    </ul>
    <li>📝 <strong>Create Playlist:</strong> <code>Create playlist</code></li>
    <ul>
        <li><code>Create me a playlist based on my love for jazz and the song Blinding Lights</code></li>
    </ul>
</ul>
"""


start_of_chat = True
def agent_response(user_input, history):
    global start_of_chat
    if start_of_chat:
        start_of_chat = False
        return instructions
    else:
        response = agent_executor(user_input)
        response = response["output"]
        return f"{response}"


demo = gr.ChatInterface(
    agent_response,
    chatbot=gr.Chatbot(height=300, label="Apollo 🎵"),
    textbox=gr.Textbox(placeholder="Let me enrich your listening experience", 
                       container=False, scale=7),
    title= "Apollo Music Bot",
    description=description,
    theme='finlaymacklon/smooth_slate',
    #theme= gr.themes.Soft(text_size="lg"),
    examples=examples,
    cache_examples=True,
    retry_btn=None,
    undo_btn="Delete Previous",
    clear_btn="Clear All",
)


if __name__ == "__main__":
    demo.launch()


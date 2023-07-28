from main import agent_executor
import gradio as gr

    
start_of_chat = True

def agent_response(user_input, history):
    global start_of_chat
    if start_of_chat:
        start_of_chat = False
        return "**Type !help for instructions, or jump right in!**"
    else:
        response = agent_executor(user_input)
        response = response["output"]
        return f"{response}"

examples = ["Play Passionfruit", "Queue some Drake", "Tell me about this song"]
description = """
<div align='center'>
    <img src='file/Eve.gif' style='opacity: 0.5;'/>
    <br/>
</div>
<p align='center'>Enter a message to begin.</p>
"""

demo = gr.ChatInterface(
    agent_response,
    chatbot=gr.Chatbot(height=300, label="Apollo 🎵"),
    textbox=gr.Textbox(placeholder="Let me play you a song", 
                       container=False, scale=7),
    title= "Music Bot",
    description=description,
    theme= gr.themes.Soft(text_size="lg"),
    #theme=gr.themes.Glass(primary_hue = "stone", text_size="lg"),
    examples=examples,
    cache_examples=True,
    retry_btn=None,
    undo_btn="Delete Previous",
    clear_btn="Clear All",
)
if __name__ == "__main__":
    demo.launch()


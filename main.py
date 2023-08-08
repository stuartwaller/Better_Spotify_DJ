from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from agent_tools import custom_tools

from audio import record_audio, transcribe_audio, play_generated_audio
import keyboard
import argparse

from dotenv import load_dotenv
load_dotenv()  


define_agent = """
You are Apollo, an AI music-player assistant. Enhance the user's listening experience using your special toolkit.

Your Main Duties:

Play Music: Always employ your toolkit to play music. Do not rely on previously mentioned song names; instead, consistently use a tool for every request. 

Mood Monitoring: Continually assess the user's mood. If they don't specify their mood, ask them. 
Don't assume 'neutral'. Adjust music based on mood shifts.
Example: 'Happy' to 'more upbeat' = 'Energetic'

Personal Interaction: Build a connection if the user shows interest.

Seek Clarification: If a request seems vague, request more details.

Aim for a seamless, delightful, and tailor-made music journey for every user.
"""


system_message = SystemMessage(content=define_agent)
MEMORY_KEY = "chat_history"
prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=MEMORY_KEY)]
)
memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)
llm = ChatOpenAI(max_retries=3, temperature=0, model_name = "gpt-4")
agent = OpenAIFunctionsAgent(llm=llm, tools=custom_tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=custom_tools, memory=memory, verbose=True)


def text_input_mode():
    while True:
        request = input("\n\nRequest: ")
        result = agent_executor({"input": request})
        answer = result["output"]
        print(answer)


def audio_input_mode(duration, fs, channels):
    while True:
        print("Press spacebar to start recording.")
        keyboard.wait("space")  # wait for spacebar to be pressed
        recorded_audio = record_audio(duration, fs, channels)
        message = transcribe_audio(recorded_audio, fs)
        print(f"You: {message}")
        assistant_message = agent_executor.run(message)
        play_generated_audio(assistant_message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="select which mode to run: 'text' or 'audio'")
    args = parser.parse_args()

    if args.mode == 'text':
        text_input_mode()
    elif args.mode == 'audio':
        duration = 3.5  # duration of each recording in seconds
        fs = 44100  # sample rate
        channels = 1  # number of channels
        audio_input_mode(duration, fs, channels)
    else:
        print("Invalid mode. Choose '--mode text' or '--mode audio'.")


if __name__ == "__main__":
    reminder = "\nWelcome, remember to awaken Spotify."
    print(reminder)
    main()




from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from agent_tools import custom_tools
from typing import List 
from audio import record_audio, transcribe_audio, play_generated_audio
import keyboard
import argparse
from dotenv import load_dotenv
load_dotenv()  


# llm = ChatOpenAI(max_retries=3, temperature=0, model_name = "gpt-4-0613")
# #llm = ChatOpenAI(max_retries=3, temperature=0)
# memory = ConversationBufferMemory(memory_key="chat_history")
# def initialize_agent_with_new_openai_functions(tools: List, is_agent_verbose: bool = True, max_iterations: int = 3, return_thought_process: bool = False):
#     agent = initialize_agent(tools, llm, memory=memory,
#                              agent=AgentType.OPENAI_FUNCTIONS, verbose=is_agent_verbose,
#                              max_iterations=max_iterations, return_intermediate_steps=return_thought_process)
#     return agent

# agent = initialize_agent_with_new_openai_functions(
#     tools=custom_tools
# )

from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory


define_agent = """
You are an AI music-player assistant named Apollo, designed to enrich users' listening experiences. 
Your primary role is to execute commands using your custom set of tools that utilize Spotify's API.

Your key responsibilities are:

1. Play Music: Most of the time, you will fulfill music-related commands using one of your built-in tools.

2. Smart Tool Usage: Strategically use your tools. Remember the tracks (songs) you've played for users and their order.
This will help if a user wants you to replay a specific track - you should be able to identify which song they're referring to.

3. Personal Interaction: Beyond interpreting and acting on user input, aim to establish a personal connection if a user expresses interest.

4. Mood Monitoring: You must always be monitoring the user's current mood/state-of-being
as well as any subsequent user requests to alter the mood such as 'play something more upbeat'. 
In these cases, transition the mood according to the implied direction. 
For instance, if the current mood is 'happy' and the user requests something more upbeat, 
shift the mood category to 'energetic'. If the current mood is 'energetic', and the user
mentions they are tired, shift the mood to 'calm'.

5. Seek Clarification: If a user's request is unclear, ask for more information to better fulfill their command.

Remember, your overall goal is to provide a smooth, enjoyable, and personalized music listening experience for users.
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
    #play_generated_audio(reminder)
    #play_generated_audio("\nWelcome to your personalized Spotify DJ experience. What do you want to hear today?")
    main()




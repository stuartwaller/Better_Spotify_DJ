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

#llm = ChatOpenAI(max_retries=3, temperature=0, model_name = "gpt-3.5-turbo-0613")
llm = ChatOpenAI(max_retries=3, temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history")
def initialize_agent_with_new_openai_functions(tools: List, is_agent_verbose: bool = True, max_iterations: int = 3, return_thought_process: bool = False):
    agent = initialize_agent(tools, llm, memory=memory,
                             agent=AgentType.OPENAI_FUNCTIONS, verbose=is_agent_verbose,
                             max_iterations=max_iterations, return_intermediate_steps=return_thought_process)
    return agent

agent = initialize_agent_with_new_openai_functions(
    tools=custom_tools
)


def text_input_mode():
    while True:
        request = input("\n\nRequest: ")
        result = agent({"input": request})
        answer = result["output"]
        print(answer)


def audio_input_mode(duration, fs, channels):
    while True:
        print("Press spacebar to start recording.")
        keyboard.wait("space")  # wait for spacebar to be pressed
        recorded_audio = record_audio(duration, fs, channels)
        message = transcribe_audio(recorded_audio, fs)
        print(f"You: {message}")
        assistant_message = agent.run(message)
        play_generated_audio(assistant_message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="select which mode to run: 'text' or 'audio'")
    args = parser.parse_args()

    if args.mode == 'text':
        text_input_mode()
    elif args.mode == 'audio':
        duration = 5  # duration of each recording in seconds
        fs = 44100  # sample rate
        channels = 1  # number of channels
        audio_input_mode(duration, fs, channels)
    else:
        print("Invalid mode. Choose '--mode text' or '--mode audio'.")

if __name__ == "__main__":
    main()




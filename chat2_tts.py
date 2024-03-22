"""
pip install pyaudio, pydub, edge_tts, slack_sdk
"""

import threading
import queue
import time

import asyncio
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from pydub import AudioSegment
from pydub.playback import play
import edge_tts
import io
import string

# Create a queue to store audio files
queue = queue.Queue(maxsize=5)

# Define a function to consume audio files, this function always runs
def play_sound():
    while True:
        # Get and play an audio file
        audio = queue.get()
        play(audio)

# Text to speech
TEXT = """Hello, world!"""
VOICE = "en-US-GuyNeural"
async def tts(TEXT):
    communicate = edge_tts.Communicate(TEXT, VOICE)
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
        # elif chunk["type"] == "WordBoundary":
        #     print(f"WordBoundary: {chunk}")
    audio_stream.seek(0)
    audio = AudioSegment.from_file(audio_stream)
    return audio

# Determine if the tts sentence is composed of pure punctuation
def is_punctuation(s):
  punctuation = set(string.punctuation + string.whitespace)
  for c in s:
    if c not in punctuation:
      return False
  return True

# Get timestamp
def get_conversations_timestamp():
    global conversations_timestamp
    # Initialize, if the configuration file does not exist, create an empty configuration file
    file_name = 'save_conversations_timestamp.ini'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write('')  
    # Get the message column identifier from the configuration file
    with open(file_name, 'r') as f:
        first_line = f.readline()  
        if not first_line:
            conversations_timestamp = None
        else:
            conversations_timestamp = first_line

# Get user input
def get_user_input():
    print('You:')
    lines = []
    while not lines:
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    return "\n".join(lines)

# Send message
def send_msg(message):
    global conversations_timestamp, last_msg_timestamp
    file_name = 'save_conversations_timestamp.ini'
    try:
        response = client.chat_postMessage(
            channel=channel_id, 
            text=message, 
            thread_ts=conversations_timestamp, 
            as_user=True
            )
    except SlackApiError as e:
        print(f"Error sending message: {e}")
    # Update the last reply timestamp of the message column
    last_msg_timestamp = response['message']['ts']
    # Whether to open a new message column (/reset implementation method)
    if not conversations_timestamp:
        conversations_timestamp = response['ts']
        # Update the message column identifier in the configuration file
        with open(file_name, 'r+') as f:
            f.seek(0)  
            f.write(conversations_timestamp)  

# Get reply
def get_print_new_msg():
    print('Claude:')
    global time_step, tts_flag
    print_new_msg = tts_new_msg = 1
    while True:
        try:
            new_msg = client.conversations_replies(
                token=userOAuthToken, 
                channel=channel_id, 
                ts=conversations_timestamp,
                oldest=last_msg_timestamp
                )
        except SlackApiError as e:
            print(f"Error sending message: {e}")
        # \n&gt; _*Please note:* 
        # When your reply is prompted by *Please note:*, there will be multiple messages, we adjust the acquisition strategy, here only get the second one (the first one is our input)
        # The length of the message is 1, not replied
        if len(new_msg['messages']) == 1: 
            continue
        idx = 1 - len(new_msg['messages'])
        new_msg = new_msg['messages'][idx]['text']
        # Not replied
        if new_msg == '_Typing…_': 
            time.sleep(time_step)
            continue
        # Start replying, print step by step
        if new_msg.endswith('_Typing…_'):
            if tts_flag:
                # Speech segmentation
                for idx,c in enumerate(new_msg[:-11][::-1]):
                    if c in ",;:!?，。；：！？\n":
                        if is_punctuation(new_msg[tts_new_msg:-11-idx]):
                            continue
                        audio = asyncio.run(tts(new_msg[tts_new_msg:-11-idx]))
                        tts_new_msg = len(new_msg)-11-idx
                        queue.put(audio)
                        break
            # Print
            print(new_msg[print_new_msg:-11], end='')
            print_new_msg = len(new_msg)-11
            time.sleep(time_step)
        else:
            if tts_flag:
                audio = asyncio.run(tts(new_msg[tts_new_msg:]))
                queue.put(audio)
            print(new_msg[print_new_msg:],end = '[END]\n\n')
            break
    return new_msg[1:]

# Main program
def chat():
    global conversations_timestamp
    get_conversations_timestamp()
    while True:
        # Get input
        message = get_user_input()
        if message == '/reset':
            conversations_timestamp = None
            print('Reset the conversation!')
            continue
        # Send input
        send_msg(f'<@{claude_id}>' + message)
        # Get, print reply
        time.sleep(time_step + 1)
        new_msg = get_print_new_msg()

# Run
if __name__ == "__main__":
    print("\n\
    ***************************************************\n\
        Hello! This program uses Slack's API to chat with Claude;\n\
        Press Enter twice to interact, please start!\n\
        Enter '/reset' to reset the conversation.\n\
    ***************************************************\n")

    # Whether to open voice 1 open, 0 close
    tts_flag = 0
    # User OAuth Token
    userOAuthToken = ''
    # Channel ID
    channel_id = ''
    # Claude ID
    claude_id = ''
    # Connect to slack
    client = WebClient(token=userOAuthToken)
    # The last reply timestamp of the message column
    last_msg_timestamp = None
    # Update reply interval
    time_step = 1

    if tts_flag:
        # Create a thread to print elements in the queue
        printer_thread = threading.Thread(target=play_sound)
        printer_thread.start()
    chat()

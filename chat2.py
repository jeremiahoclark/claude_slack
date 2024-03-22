"""
pip install slack_sdk
"""

import time
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# User OAuth Token
userOAuthToken = ''
# Channel ID
channel_id = ''
# Claude ID
claude_id = ''
# Connect to slack
client = WebClient(token=userOAuthToken)

print("""\

***************************************************
    Hello! This program uses Slack's API to chat with Claude;
    Press Enter twice to interact, please start!
    Enter '/reset' to reset the conversation.
***************************************************\

    """)

# Initialize, if the configuration file does not exist, create an empty configuration file
file_name = 'save_conversations_timestamp.ini'
if not os.path.exists(file_name):
    with open(file_name, 'w') as f:
        f.write('')  

def get_print_new_msg():
    global time_step

    len_new_msg = 1
    while True:
        try:
            new_msg = client.conversations_replies(
                token=userOAuthToken, 
                channel=channel_id, 
                # ts is empty, a new conversation will be created (/reset implementation method)
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
        if new_msg.endswith('Typing…_'):
            print(new_msg[len_new_msg:-11], end='')
            len_new_msg = len(new_msg)-11
            time.sleep(time_step)
        else:
            print(new_msg[len_new_msg:],end = '[END]\n\n')
            break
    return new_msg[1:]

def get_user_input():
    lines = []
    while not lines:
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    return "\n".join(lines)

def send_msg(message):
    global conversations_timestamp, last_msg_timestamp

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

# Get the message column identifier from the configuration file
with open(file_name, 'r') as f:
    first_line = f.readline()  
    if not first_line:
        conversations_timestamp = None
    else:
        conversations_timestamp = first_line

# The last reply timestamp of the message column
last_msg_timestamp = None
# Update reply interval
time_step = 0.5

# Main program
def chat():
    global conversations_timestamp
    while True:
        # Get input
        print('You:')
        message = get_user_input()
        if message == '/reset':
            conversations_timestamp = None
            print('Reset the conversation!')
            continue

        # Send input
        send_msg(f'<@{claude_id}>' + message)

        # Get and print reply (get is for future access to other apis, currently useless)
        print('Claude:')
        time.sleep(time_step + 1)
        new_msg = get_print_new_msg()

# Run
if __name__ == '__main__':
    chat()

# No longer available

# chat_with_slack_claude2

Difference between [chat_with_slack_claude](https://github.com/fffnower/chat_with_slack_claude):

1. Curve method, realize true reset conversation, that is, '/reset' (the principle is to abandon the original message column, open a new conversation, not sure what negative impact will be caused by opening too many message columns)

2. You need to get the member ID of Claude

3. Generally speaking, '/reset' is not needed, you can say to him, "Please forget all our previous conversations and start over.",

He will pretend to forget all, and will not reply to the context again (actually still remember); 

---

You need to install some libraries (the first three libraries are used to implement the optional voice function of chat2_tts.):

```
pip install pyaudio, pydub, edge_tts, slack_sdk
```

You need to do some settings on api.slack.com and get some parameters to call slack's api;

You need to visit the chat with Claude on the web and get some parameters to call slack's api.

You need to download the slack desktop client and get some parameters to call slack's api.

You need to fill in the parameters you get into the corresponding position of chat.py (see comments)

Please note that you cannot use "slash commands", see https://api.slack.com/interactivity/slash-commands (this project only simulates the effect of using /reset)

---

## 1. Get User OAuth Token

- Go to the website: https://api.slack.com/ --> Click on the top right corner [Your apps] --> Pop-up window [Create an app] --> Click [From scratch]

- Fill in the app name and select the workspace (example: name: Bot, workspace: chat) --> Click [Create App]

- Click on the left sidebar [OAuth & Permissions] --> Scroll down to the [Scopes] card --> Add permissions under [User Token Scopes], as follows:

  - channels:history
  - channels:read
  - chat:write
  - files:write
  - groups:history
  - groups:read
  - im:history
  - im:read
  - im:write
  - mpim:history
  - mpim:read
  - team:read
  - users:read

- Go back to the top [OAuth Tokens for Your Workspace] bar, click [Install to Workspace], and then confirm the authorization

- **Your User OAuth Token:** 

![image](https://user-images.githubusercontent.com/32289652/236893002-4ab20f60-4db8-4964-a6ce-cb5943c27c33.png)

---

## 2. Channel ID

- Open the web page and create a private channel, at this time the URL is: https://app.slack.com/client/strings1/strings2/thread/strings2-1683631995.739509 

  or https://app.slack.com/client/strings1/strings2

- **Your Channel ID:** strings2

---

## 3. claude_id

- First, you need to enter @Claude in the input box of the channel and press Enter, and agree to the application to access your channel.

- You can call the member id through the api in https://api.slack.com/events/app_mention

- Another convenient method is to download the slack desktop client, [Apps] --> Right-click on Claude --> [View App Details] --> Copy [Member ID]

- At this point, you have obtained your **claude_id:** Member ID

![image](https://github.com/fffnower/chat_with_slack_claude2/assets/32289652/c71828f5-c87b-47a2-96c8-7efa266ff838)


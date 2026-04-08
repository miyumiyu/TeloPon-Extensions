# 📺 YouTube Live+ (YoutubeLiveOAuth.py)

**[Download YoutubeLiveOAuth.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py)**

A feature-rich YouTube Live integration plugin using YouTube Data API v3 + OAuth2.  
You can read/write chat comments, create polls, change stream titles, and get viewer counts -- all through voice commands to the AI.

> This is a superior replacement for the legacy "YouTube Integration Tool (YoutubeLivePlugin.py)".  
> The legacy version only supported reading comments, but this plugin enables writing and various operations through OAuth2 authentication.

---

## Key Features

| Feature | Description |
|---|---|
| Read chat comments | Inject viewer comments into AI in real time |
| Write chat comments | AI posts messages to YouTube chat |
| Poll creation / closing / tallying | Operate YouTube's official poll feature by voice |
| Change stream title | Change the title via voice command |
| Get viewer count | Retrieve the current concurrent viewer count and have AI announce it |
| Stream selection (list / URL) | Select from a list of scheduled streams, or specify directly by URL |
| Automatic permission detection | Automatically detects whether you are the owner/manager and displays available features |

---

## Features by Permission Level

The features available to you depend on your permission level for the stream you connect to.

| Feature | Owner / Manager | Viewer / Moderator |
|---|---|---|
| Read comments | Yes | Yes |
| Write comments | Yes | Yes |
| Get viewer count | Yes | Yes |
| Polls | Yes | No |
| Change title | Yes | No |

> Permissions are automatically detected upon connection and displayed in the stream info preview.  
> Unavailable features are automatically unchecked and grayed out.

---

## Setup Steps

### Step 1: Google Cloud Console Setup (First Time Only)

For the first time, you need to create a project, enable the API, and obtain a Client ID in Google Cloud Console.  
We have prepared a detailed guide with screenshots -- please follow it.

**[Google Cloud Console Setup Guide (with screenshots)](YoutubeLiveOAuth_GCP_Setup.md)**

Guide steps:
1. Log in to Google Cloud Console
2. Create a new project
3. Configure the OAuth consent screen
4. Enable YouTube Data API v3
5. Configure scopes
6. Add test users
7. Create an OAuth Client ID -> Obtain **Client ID** and **Client Secret**
8. Enter them in TeloPon and authenticate

Once complete, the channel name and thumbnail will be displayed on TeloPon's settings screen.  
From the second time onward, authentication is already done, so this step can be skipped.

---

### Step 2: Select a Stream and Connect

After authentication, there are two ways to select a stream.

#### Method A: Select from the Stream List

1. Click the "Get Stream List" button (scheduled streams will be listed)
2. Select a stream from the list -> The title and thumbnail will be previewed
3. Click the "Connect to This Stream" button

> **The stream list only shows streams from the account you authenticated with.**  
> Even if you have manager permissions for another channel, that channel's streams will not appear in the list.  
> To connect to another channel with manager permissions, please use **Method B (Specify by URL)** below.

#### Method B: Specify by URL

1. Paste the YouTube Live URL into the input field
2. Click the "Confirm" button -> The title and thumbnail will be previewed
3. Click the "Connect to This Stream" button

> With either method, permissions are automatically detected upon connection.  
> It will display either `Permission: Owner (all features available)` or `Permission: Viewer (comments & viewer count only)`.

---

### Step 3: Start the Live Stream

On TeloPon's main screen, press **"Start Live Connection"**.

> **Important:** Please click "Connect to This Stream" **before** starting the live stream.  
> Connecting beforehand ensures that the AI reliably receives stream information and command descriptions.  
> It is also possible to connect after starting the stream, but command recognition accuracy may be slightly reduced.

---

## Voice Command Examples (Say These and the AI Will Respond)

### Writing Comments

The streamer can instruct the AI to post to YouTube chat.

| Streamer says | AI action |
|---|---|
| "Write 'Hello' in the chat" | Posts "Hello" to YouTube chat |
| "Post 'Thanks for watching today' as a comment" | Posts "Thanks for watching today" to YouTube chat |

### Polls (Owner/Manager Only)

Use YouTube's official poll feature to let viewers vote.  
You can set 2 to 4 choices.

| Streamer says | AI action |
|---|---|
| "Run a poll about favorite colors" | A poll like "What's your favorite color? Red / Blue / Green" appears in chat |
| "Take a poll on what we should do next" | AI creates a poll with appropriate choices |
| "Tally the results" / "Close the poll" | Closes the poll and AI announces the results to viewers |

> When a poll is closed, the results are fed back to the AI.  
> The AI will announce results via telop, such as "Red is in first place with 15 votes!"

### Title Change (Owner/Manager Only)

| Streamer says | AI action |
|---|---|
| "Change the title to 'Casual Chat Stream'" | The stream title is changed to "Casual Chat Stream" |
| "Change the title, make it 'Minecraft Building Episode'" | The stream title is changed to "Minecraft Building Episode" |

### Get Viewer Count

| Streamer says | AI action |
|---|---|
| "How many people are watching?" | AI retrieves the current concurrent viewer count and displays it via telop |
| "Tell me the viewer count" | Same as above |

---

## Viewer Permission Settings for Commands

Each feature has a "Viewer Allowed" checkbox.  
This controls **whether the AI can execute commands based on viewer comments**.

| Setting | Behavior |
|---|---|
| Viewer Allowed ON | If a viewer comments something like "Run a poll", the AI may execute it |
| Viewer Allowed OFF | Only executed via the streamer's voice commands. Not triggered by viewer comments |

> Please carefully consider whether to allow viewers to use high-impact operations like title changes.

---

## Feature Settings

The right side of the settings screen has ON/OFF checkboxes for each feature.

| Feature | Default | Description |
|---|---|---|
| Get comments | ON | Send viewer comments to AI |
| Write comments | ON | Allow AI to post to chat |
| Polls | ON | Create / close polls |
| Title change | ON | Change the stream title |

- Feature settings are grayed out and cannot be changed during a live stream (because injected prompts cannot be revoked)
- Features you don't have permission for are automatically unchecked and grayed out

---

## Two-Column Settings Layout

The settings screen uses a two-column layout.

### Left Column

| Section | Content |
|---|---|
| OAuth2 Authentication | Client ID / Secret input, authentication button, user info display |
| Select Stream | Get stream list, URL input, Confirm / Connect buttons |
| Stream Info Preview | Title, description, thumbnail, permission display |

### Right Column

| Section | Content |
|---|---|
| Feature Settings | ON/OFF toggle + Viewer Allowed checkbox for each feature |
| Close Button | Save settings and close the screen |

---

## Important Notes

### Connection Timing

It is recommended to click "Connect to This Stream" **before** starting the live broadcast.  
Commands will still work if you connect after starting, but the way information is communicated to the AI will differ slightly.

### OAuth Consent Screen Test Mode

The OAuth app created in Google Cloud Console can be used in "test mode".  
As long as you add your email address as a test user, no public review is required.  
In test mode, you can register up to 100 test users.

### Connecting with Manager Permissions

Even if you are not the channel owner, you can use all features if you have been invited as a "Manager" in YouTube Studio.  
However, you need to select and log in with the managed Brand Account during authentication.

### API Quota

YouTube Data API v3 has a quota limit of 10,000 units per day.  
This is more than sufficient for normal streaming, but be aware if you expect a large number of API calls.

### Using Alongside the Legacy YouTube Integration Tool

If both the legacy version (YoutubeLivePlugin.py) and this plugin (YoutubeLiveOAuth.py) are enabled simultaneously,  
comments will be sent to the AI in duplicate. Please enable only one of them.

---

[Back to Plugin List](../../../README.md#-standard-plugins-included-extension-details)

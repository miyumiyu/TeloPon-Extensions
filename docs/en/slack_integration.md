# 💬 Slack (slack_integration.py)

This plugin allows TeloPon's AI to read comments posted to your company's Slack workspace or team channels with zero delay!
It uses the latest "Socket Mode" technology, so the response is remarkably real-time.

The setup consists of three main steps: **"Step 1: Install the Plugin"**, **"Step 2: Create a Bot on Slack (Get Two Tokens)"**, and **"Step 3: Configure in the TeloPon UI"**. There are quite a few steps, but if you follow them in order, you can set it up without any issues!

---

## Step 1: Install the Plugin and Prepare

**[Download slack_integration.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py)**

1. Download the file from the link above.
2. Place the downloaded file into the **`plugins`** folder inside the TeloPon application folder.
3. Launch TeloPon. If **"Slack Comment Integration"** appears under "Extensions" on the main screen, the installation was successful!

---

## Step 2: Create a Slack Bot and Get "Two Tokens"

To allow the AI to read Slack comments, you need to create a dedicated "Bot (App)". Here you will obtain **two types of tokens (keys)**.

### 1. Create and Name the App
1. Open [Slack API (Your Apps)](https://api.slack.com/apps) in your PC browser and click **"Create New App"** in the upper right.
2. Select **"From scratch"**, enter a name of your choice (e.g., `TeloPon Integration Bot`), select the workspace you want to install it in, and click **"Create App"**.
3. **[Important]** Open **"App Home"** in the left menu, scroll down a bit to **"Your App's Presence in Slack"**, click the "Edit" button, and set the `Display Name` and `Default Username` (lowercase alphanumeric only), then save. If you skip this, you won't be able to invite the Bot!

### 2. Enable Socket Mode and Get the "App-Level Token"!
1. Open **"Socket Mode"** from the left menu.
2. Turn the **"Enable Socket Mode"** switch **ON (green)**.
3. When asked for a token name, enter something like `telopon-socket` and click "Generate".
4. A string starting with **`xapp-`** will appear. This is the **App-Level Token**. Copy it and save it somewhere.

### 3. Grant Permissions (Scopes) to Read Messages
1. Open **"OAuth & Permissions"** from the left menu.
2. Scroll down to **"Scopes"**, and under **"Bot Token Scopes"**, click "Add an OAuth Scope" and add the following 5 scopes:
   * `channels:history` / `groups:history` / `channels:read` / `groups:read` / `users:read`

### 4. Configure Real-Time Receiving (Event Subscriptions)
1. Open **"Event Subscriptions"** from the left menu.
2. Turn **"Enable Events"** at the top **ON (green)**.
3. Expand **"Subscribe to bot events"** just below, click "Add Bot User Event", add the following 2 events, and click **"Save Changes"** in the lower right:
   * `message.channels` / `message.groups`

### 5. Install to Workspace and Get the "Bot Token"!
1. Open **"Install App"** from the left menu and click **"Install to Workspace"**. (If you changed permissions, it will show "Reinstall".)
2. A permission screen will appear -- click "Allow".
3. A string starting with **`xoxb-`** will appear. This is the **Bot Token**. Copy it and save it somewhere.

### 6. [Very Important] "Invite" the Bot to a Slack Channel
Open Slack and **send a mention to the bot (e.g., `@TeloPon Integration Bot`) in the input field of the channel you want to monitor (such as #general)**. When asked "Would you like to add them to the channel?", be sure to add them. If you forget this, the bot won't be able to read comments!

---

## Step 3: Configure and Connect in the TeloPon UI

Return to TeloPon's screen and open the settings panel for "Slack Comment Integration".

![Slack integration settings screen](../images/discord_integration.png)

1. **Enter the Tokens**
   * Paste the string starting with **`xapp-`** obtained in Step 2 into the "App-Level Token" field.
   * Paste the string starting with **`xoxb-`** obtained in Step 2 into the "Bot Token" field.
2. **Get the Channel List**
   * Click the **"Verify Tokens & Get Channel List"** button.
   * If successful, a list of channels from your Slack workspace will be retrieved.
3. **Select a Channel to Monitor**
   * Choose the channel you want to monitor from the dropdown. (Public channels have a chat icon, and private channels have a lock icon.)
4. **Connect!**
   * Finally, click the blue **"Connect"** button. If the status changes to a green "Connected (Socket Mode running)", you're all set!

---

## Tips and Usage

Once setup is complete, just press "Start Live Connection (Start AI)" on TeloPon's main screen! The AI will quickly react to messages in the specified Slack channel.

* **Automatic name conversion**: Slack's unique user IDs (like U1234...) are automatically converted behind the scenes in TeloPon to the poster's display name (e.g., "John Smith") before being sent to the AI. The AI will properly address people by name when responding!
* **Customizing the prompt**: You can change the instruction text at the bottom of the settings screen to something like "These are chats from team members! Be cheerful and encouraging!" to further bring out the AI's personality.

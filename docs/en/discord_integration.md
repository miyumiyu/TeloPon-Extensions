# 💬 Discord (discord_integration.py)

This plugin allows TeloPon's AI to read and react to comments in real time from a specified channel in your Discord server!

The setup consists of three main steps: **"Step 1: Install the Plugin"**, **"Step 2: Create a Bot on Discord (Get the Token)"**, and **"Step 3: Configure in the TeloPon UI"**. Even beginners can complete it in about 5 minutes by following the steps in order!

---

## Step 1: Install the Plugin

**[Download discord_integration.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py)**

1. Download the file from the link above.
2. Open the `TeloPon-XXX` folder (the main application folder) on your computer.
3. Place the downloaded file directly into the **`plugins`** folder inside it.
4. Launch (or restart) TeloPon. If **"Discord Real-Time Integration"** appears in the "Extensions" list on the main screen, the installation was successful!

---

## Step 2: Create a Discord Bot and Get the "Token"

For the AI to read Discord comments, you need to create your own "Bot".

### 1. Access the Developer Portal
Open [Discord Developer Portal](https://discord.com/developers/applications) in your PC browser and log in with the Discord account you normally use.

### 2. Create an Application (Bot)
1. Click the **"New Application"** button in the upper right.
2. Enter a name of your choice (e.g., `TeloPon Reading Bot`) in `Name`, check the terms of service checkbox, and click **"Create"**.

### 3. [Very Important] Enable the Permission to Read Messages
**If you forget this, the bot will not be able to read comments! Be sure to configure this.**
1. Click **"Bot"** in the left-side menu.
2. Scroll down a little and find the **"Privileged Gateway Intents"** section.
3. Turn the **"Message Content Intent"** switch **ON (green)**, and if a popup appears, click "Save Changes" to save.

### 4. Copy the Token (Key)
1. Return to the top of the **"Bot"** page.
2. Click the **"Reset Token"** button next to "Token" and select "Yes, do it!".
3. A long string (this is the token) will appear -- click the **"Copy"** button to copy it.
*(Note: This string will not be shown again after closing the page, so paste it into a text editor for safekeeping)*

---

## Step 3: Configure and Connect in the TeloPon UI

From TeloPon's main screen, open "Extensions" and click the settings button for **"Discord Real-Time Integration"** to open the panel.

![Discord integration settings screen](../images/slack_integration.png)

### 1. Enter the Token
* Paste the long string (token) you copied in Step 2 into the "Bot Token" input field.

### 2. Invite the Bot to Your Server
* With the token entered, click the **"Invite This Bot to a Server"** button just below.
* A browser window will automatically open showing Discord's invitation screen.
* Select the server you want to add the bot to, then proceed with "Yes" -> "Authorize".
*(If you see a message like "XX added TeloPon Reading Bot" in Discord, it was successful!)*

### 3. Get the Channel List
* Return to TeloPon's screen and click the **"Verify Token & Get Channel List"** button.
* If successful, you will see a message like "Success: Retrieved XX channels!".

### 4. Select a Channel to Monitor
* Open the "Channel to Monitor" dropdown below, and a list of your server's channels (text channels, voice channels, etc.) will appear.
* Select the channel you want the AI to read from.

### 5. Connect!
* Finally, click the blue **"Start (Connect)"** button!
* If the status changes to "Connected" in green, you're all set!

---

## Tips and Usage

Once setup is complete, just press "Start Live Connection (Start AI)" on TeloPon's main screen as usual!
When someone posts in the specified Discord channel, the comment is sent to the AI within about 0.1 seconds, and the AI will react to it.

* **Customizing the prompt**: You can change how the AI responds by editing the "Instruction text to pass to AI" at the bottom of the settings screen. (Example: "These are comments from Discord listeners. Reply in a friendly manner!")
* **Bot going offline?**: The bot appears "Online (green dot)" on Discord only while TeloPon's "Connect" button is active. When you close TeloPon, the bot automatically goes back offline.

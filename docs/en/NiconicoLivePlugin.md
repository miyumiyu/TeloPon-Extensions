# 📺 Niconico Live (NiconicoLivePlugin.py)

📥 **[Download NiconicoLivePlugin.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/NiconicoLivePlugin.py)**

Real-time integration with Niconico Live (niconico Nama-housou). Fetches comments, gifts, Niconi-ads, polls, and viewer statistics, injecting them into the AI.  
Comment reading works without login. With login, you can also create polls and post operator comments.

---

## 🌟 Key Features

### 📖 Basic Features (No Login Required)

| Feature | Description |
|---|---|
| Comment Reading | Real-time viewer comment fetching and AI injection |
| Gift Notifications | AI expresses gratitude when gifts are received |
| Niconi-ad Notifications | AI thanks viewers for ads |
| Emotion Notifications | AI reacts when emotions surge |
| Statistics Updates | Auto-notification when viewer count hits milestones |
| Poll Result Notifications | AI comments on poll results |

### ✏️ Control Features (Login Required, Own Broadcast Only)

| Feature | Description |
|---|---|
| Create/Show/Close Polls | Create, view results, and close polls via voice commands |
| Operator Comments | Post operator comments (with color & pin support) and delete them |
| Get Viewer Count | Retrieve current concurrent viewers and comment count |

---

## ⚙️ Requirements

- Windows PC

---

## 📋 Setup

### 1. Open Settings

Click the **"⚙️ Settings"** button next to **"Niconico Live Plugin"** in the Extensions panel on the right side of TeloPon's main screen.

### 3. Connect to Niconico Live

1. Enter the Niconico Live URL (e.g., `https://live.nicovideo.jp/watch/lv350259676`)
2. Click the **"Connect"** button
3. If broadcast info (title, description, thumbnail) appears, connection is successful

> For upcoming broadcasts, the status shows "Waiting for broadcast..." and auto-connects when it starts.

### 4. Login (Optional)

To use control features (polls, operator comments), you need to log in with your Niconico account.

1. Enter your email and password in the "Niconico Login" section at the top
2. Click **"Login"**
3. If two-factor authentication is enabled, a 6-digit verification code input will appear
4. On success, your profile icon and name are displayed

> **Control features are only available on your own broadcasts.** Other broadcasts are read-only.

### 5. Feature ON/OFF

Toggle each feature individually in the right column.

**Read-only features (no login):**
- Comment reading, Gift notifications, Niconi-ad notifications
- Emotion notifications, Statistics updates, Poll result notifications

**Control features (login required):**
- Get viewer count ("Viewer OK" checkbox allows viewer comments to trigger it)
- Create/close polls
- Operator comments

---

## 🎤 Voice Commands

### Polls

| Voice Command | Action |
|---|---|
| "Create a poll" | AI creates a poll with question and choices |
| "Show results" | Display poll results |
| "Close the poll" | End the poll |

### Operator Comments

| Voice Command | Action |
|---|---|
| "Post operator comment: ○○" | Post an operator comment |
| "In red: ○○" | Post colored operator comment (white/red/pink/orange/yellow/green/cyan/blue/purple/black) |
| "Pin: ○○" | Post a pinned operator comment |
| "Delete operator comment" | Remove the operator comment |

### Information

| Voice Command | Action |
|---|---|
| "How many viewers?" | Get current concurrent viewers and comment count |

---

## 📝 How AI Injection Works

### Comments
Viewer comments are batched at intervals and sent to the AI together. Anonymous user display names can be configured.

### Gifts & Niconi-ads
When detected, the sender's name, item name, and point value are sent to the AI, prompting a thank-you message.

### Statistics Milestones
The AI is notified when viewer count surpasses 100 / 500 / 1,000 / 2,000 / 3,000 / 5,000 / 10,000 / 20,000 / 50,000 / 100,000.

### Broadcast Info
Stream title and description are added to the prompt on connection, so the AI understands the show content.

---

## ⚠️ Notes

- **Connect/disconnect during live:** This plugin is a TOOL type, so you can connect/disconnect in real-time during a stream.
- **Control features for own broadcasts only:** Even when logged in, poll creation and operator comments are disabled for other people's broadcasts (auto-grayed out).
- **Two-factor authentication supported:** Compatible with Niconico's 2FA.
---

[⬅️ Back to Extension Plugin List](../../README_en.md)

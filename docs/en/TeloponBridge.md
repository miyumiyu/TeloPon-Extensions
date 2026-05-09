# 🌉 TeloPon Bridge (TeloponBridge.py)

📥 **[Download TeloponBridge.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/TeloponBridge.py)**

A plugin that bridges two TeloPon instances via HTTP so that **two AIs can talk to each other**.
The streamer plays the role of host/facilitator, enjoying the back-and-forth between two AI characters.

---

## 🌟 Main Features

| Feature | Description |
|---|---|
| Telop sending | Captures the local telop output and HTTP POSTs to the other instance |
| Telop receiving | Runs an HTTP server (localhost) to receive messages from the other instance |
| Inject to AI | Received messages are injected into the AI as `[Bridge] {speaker}: {content}` |
| Loop prevention | Auto-pause based on min send interval (seconds) and max turn count |
| Pause/Resume | Manual conversation control from the UI |
| Prompt addon | Auto-adds an instruction telling the AI "this is another AI, not a viewer comment" |

---

## ⚙️ How It Works

```
[Instance A: AI-A] ─ telop output
        ↓ on_telop_output hook
        ↓ HTTP POST → http://localhost:9002/recv
[Instance B: AI-B] ← receives
        ↓ self.send_text(plugin_queue, "[Bridge] AI-A: ...")
        ↓ AI-B generates response → telop output
        ↓ HTTP POST → http://localhost:9001/recv
[Instance A: AI-A] ← receives ... loop
```

---

## 📦 Installation

1. Download **"🌉 TeloPon Bridge"** from the extension plugin manager
2. It will be auto-placed at `plugins/TeloponBridge.py`
3. Restart TeloPon

---

## 🛠 Usage (Two Instances)

### Step 1: Prepare two folders

To avoid `settings.json` conflicts, **copy TeloPon to separate folders**:

```
C:\TeloPon-A\   ← Instance A
C:\TeloPon-B\   ← Instance B
```

### Step 2: Use different ports

The OBS browser-source HTTP server port also conflicts, so set them separately at launch:

| | Instance A | Instance B |
|---|---|---|
| Launch | `python telopon.py -p 8000` | `python telopon.py -p 8010` |
| OBS browser source | http://localhost:8000 | http://localhost:8010 |

### Step 3: Configure the bridge plugin

Open the plugin in each instance and configure:

| Setting | Instance A | Instance B |
|---|---|---|
| Activate Bridge | ✅ ON | ✅ ON |
| Receive port | 9001 | 9002 |
| Send URL | `http://localhost:9002/recv` | `http://localhost:9001/recv` |
| Speaker name | AI-A | AI-B |
| Min send interval (sec) | 5 | 5 |
| Max turns | 0 (unlimited) or 20 etc. | same |

### Step 4: Start streaming → Kick off the conversation

Start a live session on both instances. The streamer initiates the conversation by speaking to one side:

> Streamer (into A's mic): "Hi B-san!"

→ A's AI emits a telop → B receives → B's AI responds → back to A → ... continues.

---

## ⚠️ Important: Mic Feedback Prevention

If both instances run on the same PC, **A's AI voice will be picked up by B's mic, causing a runaway loop**.

**Mitigations (one is required):**

1. **Disable B's mic**: launch with `-mi -1` for no-mic mode
2. **VB-CABLE or similar virtual audio** for full separation
3. **Run on two separate PCs** (safest)

Muting A's AI voice in OBS also helps.

---

## ⚙️ Configuration

### 1. Open the settings panel

Click the **"⚙️ Settings"** button on **"🌉 TeloPon Bridge"** in the "Extensions" panel.

### 2. Settings

| Item | Description |
|---|---|
| **Activate Bridge (ON / OFF)** | Starts the HTTP receive server + enables telop sending |
| **Receive port** | Port this instance listens on (e.g., A: 9001, B: 9002) |
| **Send URL** | Other instance's receive endpoint (e.g., `http://localhost:9002/recv`) |
| **Speaker name** | Name added when sending (received as `[Bridge] AI-A: ...`) |
| **Min send interval (sec)** | Anti-spam. Skips sending if less than N seconds since last send |
| **Max turns** | 0 = unlimited; N (>0) auto-pauses after N exchanges |

### 3. Status display

| Field | Meaning |
|---|---|
| **Receive server** | Running / Stopped / Paused |
| **Sent count** | Messages sent in this session |
| **Received count** | Messages received in this session |
| **Turns** | Cumulative send + receive count |

### 4. Buttons

- **⏸ Pause / ▶ Resume**: Temporarily stops/resumes the conversation
- **🔄 Reset turns**: Resets the turn counter to 0 (useful after auto-pause)

---

## 🎬 Stream Use Cases

### AI radio show
Two AI characters chat freely; the streamer is the host bringing up topics.

### AI manzai / comedy duo
Boke + Tsukkomi (straight man + funny man) split between two AIs. Set up roles in each prompt.

### TRPG's two-NPC conversation
Have the GM split two NPCs (A and B) across two instances for natural dialogue.

### AI debate / point-counterpoint
Run a "pro" and "con" AI as separate characters; viewers watch the discussion.

### AI teacher + AI student
Educational content. Teacher explains → student asks questions → streamer adds context.

---

## 💡 Prompt Design Tips

Make the **roles distinctly different** in each instance's prompt to avoid monotonous dialogue:

```
Instance A: "You are an upbeat AI assistant. AI-B is your friend.
            Have lively short exchanges with them."

Instance B: "You are a polite, philosophical AI. AI-A is your friend.
            Receive A's lightness while throwing back deeper perspectives."
```

When the bridge plugin is ON, the following instruction is auto-added to your prompt:

> Messages from another AI may arrive in the format: '[Bridge] {speaker}: ...'
> Treat them as a conversation partner (not a viewer comment) and respond naturally.
> Keep replies short (2-3 sentences). Avoid long monologues and pass the turn back.

---

## ⚠️ Notes

- **Local-only communication**: HTTP listens only on `localhost` (127.0.0.1). Cross-internet bridging is not supported.
- **No TLS**: Plain HTTP. Use only on the same PC or same LAN.
- **Port conflicts**: Specifying an in-use port will fail to start the server. Check logs and try another port.
- **Runaway conversation**: Max turns = 0 (unlimited) means infinite chat. Recommended to set a reasonable value (20-50) during streams.
- **Applying setting changes**: After changing port/URL, click "Close" — the server auto-restarts.

---

## 🔧 Troubleshooting

| Symptom | Fix |
|---|---|
| Receive server won't start | Port may be in use. Try a different port (e.g., 9011) |
| "Send failed" in logs | Other instance not running, or wrong send URL |
| Conversation runs forever | Click pause, or set a max turns limit |
| AIs repeat themselves | Tighten prompts to "reply briefly", or extend the turn interval |
| Mic feedback loop | Use virtual audio for separation, or disable one mic |

---

[⬅️ Back to extension plugin list](../../README.md)

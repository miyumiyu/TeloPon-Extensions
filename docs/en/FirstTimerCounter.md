# ✨ First-Timer Counter (FirstTimerCounter.py)

📥 **[Download FirstTimerCounter.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/FirstTimerCounter.py)**

A plugin that detects keywords like "first time" or "hello" in stream comments and **displays the cumulative count of first-time viewers in a persistent status window**.
Works with any platform that provides comments — YouTube Live, Twitch, Niconico Live, etc.

---

## 🌟 Main Features

| Feature | Description |
|---|---|
| First-timer detection | Auto-counts when a configured keyword appears in a comment |
| Duplicate prevention | The same viewer is counted only once (multiple "first time" messages from the same person don't increment the counter) |
| Always-on display | Count is shown in `window-status` (a persistent window) |
| Editable keywords | Add/remove detection words freely (one per line) |
| Custom header text | Change the "✨ First-timers" header to anything you like |
| Counter clear | Reset button to start over from zero |
| Persistence | Count and known-users list saved to `plugins/first_timer_counter.json` |
| Multi-platform | Aggregates notifications from any comment-receiving plugin |

---

## ⚙️ How It Works

```
Streaming platform plugin (e.g., YouTube Live+) receives a comment
       ↓
 Calls broadcast_comment(text, author, source)
       ↓
 FirstTimerCounter.on_comment_received() is called
       ↓
 1. Check if author is already known → skip if known
 2. Match keywords (case-insensitive)
 3. If matched, increment count and add author to known list
 4. Show "✨ First-timers: N" in window-status
```

This plugin uses the **`on_comment_received` hook** (added in v2.30b), so no modification of comment-receiving plugins is required.

---

## 📦 Installation

1. Download **"✨ First-Timer Counter"** from the extension plugin manager
2. It will be auto-placed at `plugins/FirstTimerCounter.py`
3. Restart TeloPon

---

## ⚙️ Configuration

### 1. Open the settings panel

In the "Extensions" panel on the right of TeloPon's main screen, click the **"⚙️ Settings"** button on **"✨ First-Timer Counter"**.

### 2. Settings

| Item | Description |
|---|---|
| **ON / OFF** | Enable/disable the counter (turning OFF also hides the status window) |
| **Header text** | Text shown on the upper line of the telop (default: `✨ First-timers`). Leave empty to use the i18n default |
| **Detection keywords** | Keywords that, when contained in a comment, trigger the counter. One per line. Defaults: `初見` / `おはつ` / `はじめまして` / `初コメ` / `first time` / `新人` |
| **Current count** | Cumulative number of first-timers detected so far |
| **Known users** | Number of authors recorded for duplicate-prevention (may not match the count: includes authors whose comments didn't match keywords) |
| **🗑️ Clear counter** | Reset both the count and the known-users set |
| **Close** | Save settings and close the panel |

### 3. Adjust position/size in OBS

You can manipulate the status window directly on the OBS browser source:

- **Drag** — Move the position
- **Mouse wheel** — Zoom in/out
- **Double-click** — Temporarily hide (re-shown on next update)

These adjustments are saved in browser localStorage (preserved even after OBS restart).

---

## 💡 Testing

### End-to-end test

1. Start TeloPon in **debug mode**: `python telopon.py -d`
2. Connect a comment-receiving plugin (YouTube Live / Twitch, etc.)
3. Post a test comment (e.g., `first time here!`)
4. The status window should show "✨ First-timers: 1"

---

## 🔧 Advanced Usage

### Adding more keywords

For multilingual streams:

```
初見
おはつ
はじめまして
初コメ
new here
first time
just joined
hello everyone
```

### Reset known-users to recount

If you want the "first-timers of this stream" to be displayed per stream, click the **🗑️ Clear counter** button before going live.

### Persistent across sessions

By design, `stop()` does not clear the status window — the count carries over to the next session. To reset per stream, clear it manually.

---

## 📋 Use Cases

### TRPG streams

Welcome first-time players and tally their arrivals on screen. Visualizing the counter creates a viewer-participatory atmosphere.

### Large collab streams

For events with more new viewers than usual, visualize the inflow on the day. After the stream you can reflect: "Today we welcomed N first-timers!"

### Channel anniversary

Use as a milestone event for long-running streams. Reset the counter before going live to showcase new viewers in real time.

---

## ⚠️ Notes

- **Supported platforms**: Comment-receiving plugins must call `broadcast_comment()`. The bundled YouTube Live / YouTube Live+ / Twitch / Niconico Live plugins support this (since v2.30b).
- **Keyword case-sensitivity**: Case-insensitive (`First Time` and `first time` are treated the same)
- **Duplicate detection**: Based on the comment author name. The same person posting from different accounts will be counted as different people.
- **Conflict with other status uses**: `window-status` only has one slot per page. Using it alongside other persistent displays (e.g., TRPG status) will overwrite each other.

---

[⬅️ Back to extension plugin list](../../README.md)

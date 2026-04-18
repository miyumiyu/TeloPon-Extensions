# 🔊 Telop TTS - Gemini TTS (GeminiTTS.py)

📥 **[Download GeminiTTS.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/GeminiTTS.py)**

A high-quality telop TTS plugin powered by the latest **Gemini 3.1 Flash TTS Preview**.  
It reuses the Gemini API key already set in TeloPon — **no extra signup or authentication required**.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| Automatic TTS | Speaks the MAIN text output by the AI automatically |
| 30 preset voices | Kore / Puck / Zephyr / Charon / Fenrir and more |
| Emotion (badge) linkage | Reading style changes based on the AI's emotion tag |
| Character instructions | Free-text, e.g. `tsundere style`, `cheerful girl`, `calm gentleman` |
| Speed control | Slow / Normal / Fast |
| Output device | Selectable (supports virtual devices like VB-CABLE) |
| Volume | 0–100% slider |
| Delay | Wait time between telop display and TTS start |
| TOPIC readout | Toggle whether to read the TOPIC heading |
| Model selection | Gemini 3.1 Flash TTS Preview / Gemini 2.5 Flash Preview TTS |

---

## ⚠️ Important Notice

> **Gemini TTS API has strict rate limits. On the free tier, you'll hit the limit after about 5 calls.**
>
> Not suitable for long-running streams. Please use it as a **trial/demo** experience.  
> For serious use, consider the paid Gemini API (pay-as-you-go).

When you hit the rate limit, the plugin status shows "⚠️ Rate limit reached (retry in Xs)", the queue is cleared, and it waits for the specified time.

---

## ⚙️ Setup

### 1. Prerequisite
A **Gemini API key** must already be configured in TeloPon.  
This plugin reuses that configuration.

### 2. Open the settings
Click **⚙️ Settings** next to **Gemini TTS** in the Extensions panel on TeloPon's main screen.

### 3. Configure options

| Item | Description |
|---|---|
| **ON / OFF** | Enable TTS when checked |
| **Read TOPIC** | Also read the TOPIC heading |
| **Voice** | Choose from 30 preset voices |
| **Output device** | Where the audio plays (use virtual devices for OBS routing) |
| **Character** | Free text, e.g. `tsundere`, `cheerful girl`, `calm gentleman` |
| **Speed** | Slow / Normal / Fast |
| **Volume** | 0–100% |
| **Delay** | Seconds between telop display and TTS start (0–10s) |

### 4. Test playback
Use the "▶ Test" button to preview your settings.

---

## 🎭 Expressive Output

Gemini TTS supports natural-language performance direction.  
Whatever you type into "Character" is passed directly into the prompt.

### Character example

```
tsundere style
→ "tsundere style, sounding happy, at a fast pace, please read: TEXT"
```

The AI-provided `[BDG]` emotion tag is combined automatically:

- `[BDG]happy` + Character "tsundere style" + Speed "fast"
- → prompt: "tsundere style, sounding happy, at a fast pace"

Leaving Character empty is fine — only emotion & speed will be applied.

---

## 🎧 Routing Audio into OBS

To put the TTS voice on your broadcast, use a virtual audio device.

1. Install **VB-CABLE** (or similar virtual audio device)
2. In the plugin's "Output device", select the virtual input (e.g. `CABLE Input`)
3. In OBS, add an Audio Input Capture source and select the virtual output (e.g. `CABLE Output`)

---

## 💡 Choosing a Voice

30 preset voices are available. Each works in both Japanese and English with natural pronunciation.

Popular voices:
- **Kore** — calm female voice (default)
- **Puck** — bright, lively
- **Zephyr** — soft, mellow
- **Charon** — deep male voice
- **Fenrir** — powerful male voice

Use the Test button to compare and pick your favorite.

---

## ⚠️ Usage Notes

- **Live-editable:** This is a TOOL plugin — voice, character instruction, speed etc. can be changed in real time during a live session.
- **Watch rate limits:** On the free tier, rapid repeated use triggers throttling. See the notice above.
- **No streaming:** Gemini TTS API does not support streaming playback, so there is a 1–3 second delay between telop output and audio playback.

---

[⬅️ Back to Extensions](../../README_en.md)

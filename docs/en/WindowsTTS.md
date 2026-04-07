# Windows Text-to-Speech Plugin (WindowsTTS.py)

**[Download WindowsTTS.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py)**

This plugin uses the Windows built-in speech synthesis engine (SAPI5) to automatically read aloud the text of telops output by the AI.  
No additional external software is needed -- it works directly with the voices that come standard with Windows.

---

## Key Features

| Feature | Description |
|---|---|
| Automatic telop reading | Automatically converts AI-generated MAIN text to speech |
| Voice selection | Choose from voices installed on Windows (Japanese/English, etc.) |
| Playback device selection | Specify the output device (supports virtual devices like VB-CABLE) |
| Speed adjustment | Adjust reading speed with a slider |
| Pitch adjustment | Adjust voice pitch with a slider |
| Volume adjustment | Adjust reading volume with a slider |
| TOPIC reading | Toggle whether to also read the telop heading (TOPIC) |
| Emoji removal | Automatically excludes Unicode emojis and `:emoji:` format text from reading |

---

## Settings

### 1. Open the Settings Screen

On TeloPon's main screen, in the "Extensions" panel on the right side, click the **"Settings"** button for **"Windows TTS"**.

### 2. Configure Each Option

<img src="../images/WindowsTTS.png" width="400">

| Option | Description |
|---|---|
| **TTS ON** | Check this to enable text-to-speech reading |
| **Voice** | Select the voice for reading. For Japanese, "Microsoft Haruka Desktop - Japanese" is commonly used |
| **Playback Device** | Choose the audio output device. "Default Device" is the default output set in Windows |
| **Speed** | Adjust reading speed (100 = slow to 350 = fast, default 200) |
| **Pitch** | Adjust voice pitch (-10 = low to +10 = high, default 0) |
| **Volume** | Adjust reading volume (0 to 100, default 100) |
| **Also read TOPIC** | When checked, the telop heading (TOPIC) will also be read aloud |

### 3. Test Reading

Press the "Test Reading" button to play a test voice with the current settings.  
If it sounds good, click "Close" to save the settings.

---

## Routing Audio to OBS

To include the AI's text-to-speech audio in your OBS broadcast, use a virtual audio device.

### Steps

1. Install a virtual audio device such as **VB-CABLE**
2. In the WindowsTTS plugin, select the virtual device (e.g., `CABLE Input`) as the "Playback Device"
3. In OBS, add an "Audio Input Capture" and select the virtual device (e.g., `CABLE Output`)

This routes the AI's text-to-speech audio into OBS, making it part of your broadcast.

---

## About Emoji Removal

Emojis included in telops are automatically excluded from reading.

| Type | Example | Behavior |
|---|---|---|
| Unicode emojis | (game controller) (fire) (speech bubble) | Removed (not read) |
| Text emojis | `:fire:` `:thumbsup:` | Removed (not read) |
| Normal text | Hello | Read as-is |

---

## Important Notes

- **Settings can be changed during a live stream:** This plugin is a TOOL type, so speed, voice, device, and other settings can be changed in real time during a broadcast.
- **Windows only:** SAPI5 is a Windows-exclusive speech synthesis engine. It does not work on macOS/Linux.
- **Adding voices:** You can install additional voice packs from Windows "Settings" -> "Time & Language" -> "Speech".

---

[Back to Extension Plugin List](../../README.md)

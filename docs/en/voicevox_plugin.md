# VOICEVOX Text-to-Speech (voicevox_plugin.py)

**[Download voicevox_plugin.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py)**

This plugin reads aloud AI-generated telop text using the **VOICEVOX** speech synthesis engine.
With a variety of character voices and fine-tuned audio adjustments, you can make your streams more lively and entertaining.

---

## Preparation: Installing and Starting VOICEVOX

You need to install and run VOICEVOX separately from TeloPon.

1. Download and install VOICEVOX from the **[VOICEVOX official website](https://voicevox.hiroshiba.jp/)**.
2. **Start VOICEVOX**. When launched, it starts an internal HTTP server (default: `http://localhost:50021`).
3. Keep VOICEVOX **running at the same time as TeloPon**.

> VOICEVOX's window can be minimized -- it works in the background.

---

## TeloPon Settings and Usage

### 1. Open the Control Panel

On TeloPon's main screen, in the "Extensions (Plugins)" panel on the right side, click the **"Control Panel"** button for **"VOICEVOX Text-to-Speech"**.

![VOICEVOX Text-to-Speech settings screen](../images/voicevox_plugin.png)

---

### 2. Connection Test

1. Enter the VOICEVOX address in the **URL** field (default: `http://localhost:50021`)
2. Click the **"Connection Test"** button
3. If "Connection successful" appears, you're ready to go

> If the connection fails, check that VOICEVOX is running. When the connection cannot be established, audio settings will be grayed out and inaccessible.

### 3. Enable TTS

Check the **"TTS ON"** checkbox. This will automatically start reading aloud every time a telop is displayed.

### 4. Select Character and Style

After a successful connection test, a dropdown list of characters registered in VOICEVOX will appear.

* **Character**: Select the voice character for reading (e.g., Shikoku Metan, Zundamon, etc.)
* **Style**: Each character has multiple styles (e.g., Normal, Sweet, Tsundere, etc.)

When you select a character, their icon image will be displayed on the left.

### 5. Adjust Audio Parameters

| Parameter | Range | Default | Description |
|---|---|---|---|
| **Speed** | 0.5 - 2.0 | 1.0 | Reading speed. Higher values mean faster speech |
| **Volume** | 0.1 - 2.0 | 1.0 | Reading volume |
| **Pitch** | -0.15 - 0.15 | 0.0 | Voice pitch. + for higher, - for lower |
| **Intonation** | 0.0 - 2.0 | 1.0 | Emotional intensity. 0 for monotone, higher for more expressive |
| **Pre-speech silence** | 0.0 - 1.5 sec | 0.1 | Pause before reading starts (in seconds) |

> Parameters are applied in real time. New values take effect from the next telop reading.

### 6. Telop Settings

* **Also read TOPIC**: When enabled, reads in the format "TOPIC. MAIN". When disabled, reads MAIN only.
* **Telop delay (seconds)**: Delays the telop display to OBS (0 = immediate display). Use this when you want to synchronize the reading voice with the telop display timing.

### 7. Close

Click the **"Close"** button or the window's **X** button to close the settings panel. Settings are automatically saved to `plugins/voicevox.json` and restored on next launch.

---

## Troubleshooting

### Q. "Connection failed" appears during the connection test
- Check that VOICEVOX is running
- Check that the URL is `http://localhost:50021`
- Check that security software is not blocking port 50021

### Q. Reading suddenly stopped
- VOICEVOX may have been closed. If the connection is lost during reading, TTS is automatically turned OFF
- Restart VOICEVOX and reconnect using "Connection Test" in the control panel

### Q. I can't hear anything
- Check that your computer's volume is not muted
- Check that the "TTS ON" checkbox is enabled
- Check that the volume parameter is 0.1 or higher

---

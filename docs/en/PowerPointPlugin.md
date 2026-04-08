# 📊 PowerPoint Control (PowerPointPlugin.py)

📥 **[Download PowerPointPlugin.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/PowerPointPlugin.py)**

Control PowerPoint slideshows using voice commands during your stream.  
Supports slide navigation, page jumps, blackout, and automatically injects slide titles and notes to the AI when slides change.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| Next/Previous Slide | Say "next slide" or "go back" to navigate |
| Page Jump | Say "go to page 3" to jump to a specific slide |
| First/Last Slide | Say "go to the first slide" or "last slide" to jump to start/end |
| Start/End Slideshow | Say "start the presentation" or "end the presentation" |
| Screen Blackout | Say "black screen" to blank the display, "resume" to restore |
| Slide Note Injection | Automatically sends slide title and notes to AI when slides change |

---

## ⚙️ Requirements

- Windows PC
- Microsoft PowerPoint installed

---

## 📋 Setup

### 1. Open Settings

Click the **"⚙️ Settings"** button next to **"PowerPoint Control"** in the Extensions panel on the right side of TeloPon's main screen.

### 2. Connect to PowerPoint

1. Open the PowerPoint file you want to control beforehand
2. Click the **"Connect to PowerPoint"** button in the settings window
3. If you see "Connected: filename.pptx", the connection is successful

### 3. Configure Options

| Option | Description |
|---|---|
| **PowerPoint Integration ON** | Enable the plugin |
| **Inject slide notes to AI** | When ON, sends presenter notes to the AI when slides change |
| **Inject slide title to AI** | When ON, sends the slide title text to the AI when slides change |

### 4. Test Buttons

Use "Next (Test)" and "Previous (Test)" buttons to verify operation during a slideshow.

---

## 🎤 Voice Commands

During a stream, say the following to control slides:

| Voice Command | Action |
|---|---|
| "Next slide" / "Next" | Go to next slide |
| "Previous slide" / "Go back" | Go to previous slide |
| "Go to page 3" / "Jump to slide 5" | Jump to specific page |
| "Go to the first slide" | Jump to first slide |
| "Last slide" | Jump to last slide |
| "Start the presentation" | Begin slideshow |
| "End the presentation" | Exit slideshow |
| "Black screen" / "Blackout" | Blank the screen |
| "Resume" / "Restore screen" | Restore from blackout |

---

## 📝 Slide Note Injection

Each time a slide changes, the following information is automatically sent to the AI:

```
[Presentation Notes]
Slide 3/15: Slide Title
Your presenter notes text goes here...
```

This allows the AI to understand the current slide content and provide relevant commentary aligned with your presentation flow.  
Adding notes like "emphasize this point" or "add humor here" in your presenter notes will guide the AI's reactions.

---

## ⚠️ Notes

- **Connect/disconnect during live:** This plugin is a TOOL type, so you can connect/disconnect to PowerPoint in real-time during a stream.
- **Windows only:** Uses COM automation to control PowerPoint, so it works only on Windows.
- **Open PowerPoint first:** You must open a PowerPoint file before connecting.
- **Slideshow mode required:** Slide navigation commands only work during an active slideshow.
- **Viewer commands disabled:** For security, viewer comments cannot trigger slide operations (streamer voice only).

---

[⬅️ Back to Extension Plugin List](../../README_en.md)

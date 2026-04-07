[日本語](README.md) | [한국어](README_ko.md) | [Русский](README_ru.md)

# TeloPon Extensions

Extension pack for TeloPon. Provides optional features such as plugins, prompts, and themes not included in the standard distribution.

📖 [TeloPon Main Documentation](https://github.com/miyumiyu/TeloPon)

---

## Installation

Copy the files you want to use into the corresponding TeloPon folder.

| Type | Source | Destination |
|---|---|---|
| Plugins | `plugins/*.py` | TeloPon's `plugins/` folder |
| Prompts | `prompts/en/*.txt` | TeloPon's `prompts/en/` folder |
| Themes | `themes/*.css` | TeloPon's `themes/` folder |

> **For developers:** Place as a submodule `ex-plugins/` in TeloPon-dev for automatic loading.

---

## Plugin List

| | Plugin | Ver | Description | DL |
|---|---|---|---|---|
| ▶️ | [YouTube OAuth](docs/en/YoutubeLiveOAuth.md) | 1.00 | Advanced YouTube integration with YouTube Data API + OAuth2.<br>Comment read/write, polls, title change, viewer count, and more.<br>👉 [Details](docs/en/YoutubeLiveOAuth.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py) |
| 🔊 | [Windows TTS](docs/en/WindowsTTS.md) | 1.00 | Auto text-to-speech using Windows built-in SAPI5 engine.<br>Voice, speed, pitch, volume, and output device selection.<br>👉 [Details](docs/en/WindowsTTS.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py) |
| 🎮 | [VCI OSC Telop](docs/en/VciOscPlugin.md) | 1.00 | Send telops to [VirtualCast](https://virtualcast.jp/) VCI via OSC.<br>Display AI telops in VR space.<br>👉 [Details](docs/en/VciOscPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py) |
| 💬 | [Discord](docs/en/discord_integration.md) | 1.00 | Real-time comment fetching from [Discord](https://discord.com/) server channels.<br>Auto invite URL generation included.<br>👉 [Details](docs/en/discord_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py) |
| 🏢 | [Slack](docs/en/slack_integration.md) | 1.00 | Zero-delay real-time comment fetching from [Slack](https://slack.com/) channels via Socket Mode.<br>Auto user ID to name conversion.<br>👉 [Details](docs/en/slack_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py) |
| 🗣️ | [VOICEVOX TTS](docs/en/voicevox_plugin.md) | 1.00 | Text-to-speech using [VOICEVOX](https://voicevox.hiroshiba.jp/) engine.<br>Multiple character voices and styles supported.<br>👉 [Details](docs/en/voicevox_plugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py) |
| 📊 | [PowerPoint Control](docs/en/PowerPointPlugin.md) | 1.00 | Control PowerPoint slideshow by voice commands.<br>Next/prev slide, page jump, blackout, start/end presentation.<br>Auto-injects slide title and notes to AI on slide change.<br>👉 [Details](docs/en/PowerPointPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/PowerPointPlugin.py) |
| 📺 | [Niconico Live](docs/en/NiconicoLivePlugin.md) | 1.00 | Real-time comments, gifts, Niconi-ads, polls, and statistics from Niconico Live.<br>With login: create polls, post operator comments.<br>👉 [Details](docs/en/NiconicoLivePlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/NiconicoLivePlugin.py) |

---

## Prompts

(Coming soon)

## Themes

(Coming soon)

---

## License

Follows the same license as the TeloPon main application.

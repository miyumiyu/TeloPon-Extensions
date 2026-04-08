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
| 📺 | [YouTube Live+](docs/en/YoutubeLiveOAuth.md) | 1.00 | YouTube OAuth. Comment read/write, polls, title change, viewer count.<br>👉 [Details](docs/en/YoutubeLiveOAuth.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py) |
| 📺 | [Niconico Live](docs/en/NiconicoLivePlugin.md) | 1.00 | Niconico live comments, gifts, ads, polls & stats in real-time. Operator comments supported.<br>👉 [Details](docs/en/NiconicoLivePlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/NiconicoLivePlugin.py) |
| 🐦 | [X (Twitter)](docs/en/XTwitterPlugin.md) | 1.00 | Hashtag fetch, tweet with text/thumbnail/screen capture. Paid API (Pay Per Use).<br>👉 [Details](docs/en/XTwitterPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py) |
| 🔊 | [Telop TTS (Windows)](docs/en/WindowsTTS.md) | 1.00 | Auto text-to-speech with Windows SAPI5.<br>👉 [Details](docs/en/WindowsTTS.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py) |
| 🔊 | [Telop TTS (VOICEVOX)](docs/en/voicevox_plugin.md) | 1.00 | Text-to-speech with VOICEVOX. Multiple character voices.<br>👉 [Details](docs/en/voicevox_plugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py) |
| 📊 | [PowerPoint Control](docs/en/PowerPointPlugin.md) | 1.00 | Control slideshow by voice. Auto-inject slide notes.<br>👉 [Details](docs/en/PowerPointPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/PowerPointPlugin.py) |
| 💬 | [Discord](docs/en/discord_integration.md) | 1.00 | Real-time Discord channel comments.<br>👉 [Details](docs/en/discord_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py) |
| 💬 | [Slack](docs/en/slack_integration.md) | 1.00 | Real-time Slack channel comments.<br>👉 [Details](docs/en/slack_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py) |
| 🎮 | [VCI Telop Sender](docs/en/VciOscPlugin.md) | 1.01 | Send telops to VirtualCast VCI via OSC.<br>👉 [Details](docs/en/VciOscPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py) |

---

## Prompts

(Coming soon)

## Themes

(Coming soon)

---

## License

Follows the same license as the TeloPon main application.

# TeloPon Extensions

TeloPon の拡張パックです。プラグイン・プロンプト・テーマなど、標準に同梱されないオプション機能を提供します。

[English](README_en.md) | [한국어](README_ko.md) | [Русский](README_ru.md)

---

## インストール方法

使いたいファイルを TeloPon の該当フォルダにコピーしてください。

| 種類 | コピー元 | コピー先 |
|---|---|---|
| プラグイン | `plugins/*.py` | TeloPon の `plugins/` フォルダ |
| プロンプト | `prompts/ja/*.txt` | TeloPon の `prompts/ja/` フォルダ |
| テーマ | `themes/*.css` | TeloPon の `themes/` フォルダ |

> **開発者向け:** TeloPon-dev のサブモジュールとして `ex-plugins/` に配置すると、自動的に読み込まれます。

---

## プラグイン一覧

| プラグイン | 説明 | 必要ライブラリ | 詳細 |
|---|---|---|---|
| WindowsTTS | Windows標準音声で読み上げ | pyttsx3 | [詳細](docs/ja/WindowsTTS.md) |
| TelopTTS | Gemini TTSで読み上げ | - | [詳細](docs/ja/TelopTTS.md) |
| VciOscPlugin | VirtualCast VCI へOSC送信 | python-osc | [詳細](docs/ja/VciOscPlugin.md) |
| discord_integration | Discordチャンネル連携 | discord.py | [詳細](docs/ja/discord_integration.md) |
| slack_integration | Slackチャンネル連携 | slack_sdk | [詳細](docs/ja/slack_integration.md) |
| voicevox_plugin | VOICEVOX音声合成 | - | [詳細](docs/ja/voicevox_plugin.md) |

## プロンプト一覧

（準備中）

## テーマ一覧

（準備中）

---

## ライセンス

TeloPon 本体と同じライセンスに従います。

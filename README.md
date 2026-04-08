[English](README_en.md) | [한국어](README_ko.md) | [Русский](README_ru.md)

# TeloPon Extensions

TeloPon の拡張パックです。プラグイン・プロンプト・テーマなど、標準に同梱されないオプション機能を提供します。

📖 [TeloPon 本体のドキュメントはこちら](https://github.com/miyumiyu/TeloPon)

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

| | プラグイン | Ver | 説明 | DL |
|---|---|---|---|---|
| ▶️ | [YouTube OAuth連携](docs/ja/YoutubeLiveOAuth.md) | 1.00 | YouTube Data API + OAuth2 による高機能連携。<br>コメントの読み書き、アンケート作成・集計、配信タイトル変更、視聴者数取得など。<br>👉 [詳細はこちら](docs/ja/YoutubeLiveOAuth.md) / [GCP設定ガイド](docs/ja/YoutubeLiveOAuth_GCP_Setup.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py) |
| 🔊 | [Windows TTS](docs/ja/WindowsTTS.md) | 1.00 | Windows標準の音声合成エンジン（SAPI5）でテロップを自動読み上げ。<br>音声・速度・ピッチ・音量の調整、再生デバイスの選択に対応。<br>👉 [詳細はこちら](docs/ja/WindowsTTS.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py) |
| 🎮 | [VCI OSC テロップ](docs/ja/VciOscPlugin.md) | 1.01 | [VirtualCast](https://virtualcast.jp/) の VCI に OSC でテロップを送信。<br>VR空間内にAIのテロップを表示できます。<br>👉 [詳細はこちら](docs/ja/VciOscPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py) |
| 💬 | [Discord連携](docs/ja/discord_integration.md) | 1.00 | [Discord](https://discord.com/) サーバーの指定チャンネルのコメントをリアルタイムに取得し、AIに注入。<br>招待URL自動生成機能付き。<br>👉 [詳細はこちら](docs/ja/discord_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py) |
| 🏢 | [Slack連携](docs/ja/slack_integration.md) | 1.00 | [Slack](https://slack.com/) ワークスペースの指定チャンネルのコメントを Socket Mode で遅延ゼロ取得。<br>ユーザーID→名前の自動変換付き。<br>👉 [詳細はこちら](docs/ja/slack_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py) |
| 🗣️ | [VOICEVOX 読み上げ](docs/ja/voicevox_plugin.md) | 1.00 | [VOICEVOX](https://voicevox.hiroshiba.jp/) の音声合成エンジンでテロップを読み上げ。<br>多数のキャラクターボイスとスタイルに対応。<br>👉 [詳細はこちら](docs/ja/voicevox_plugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py) |
| 📊 | [PowerPoint操作](docs/ja/PowerPointPlugin.md) | 1.00 | 音声指示でPowerPointスライドショーを操作。<br>スライド送り/戻し、ページジャンプ、ブラックアウト、プレゼン開始/終了。<br>スライド切替時にタイトル・ノートをAIに自動注入。<br>👉 [詳細はこちら](docs/ja/PowerPointPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/PowerPointPlugin.py) |
| 🐦 | [X (Twitter) 連携](docs/ja/XTwitterPlugin.md) | 1.00 | ハッシュタグのツイートを定期取得してAIに注入。<br>AIが配信中にツイートを自動投稿。X Developer Portal のAPIキーが必要（有料）。<br>👉 [詳細はこちら](docs/ja/XTwitterPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py) |

---

## プロンプト一覧

（準備中）

## テーマ一覧

（準備中）

---

## ライセンス

TeloPon 本体と同じライセンスに従います。

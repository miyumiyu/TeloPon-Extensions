[English](README_en.md) | [한국어](README_ko.md) | [Русский](README_ru.md)

# TeloPon Extensions

TeloPon の拡張パックです。プラグイン・プロンプト・テーマなど、標準に同梱されないオプション機能を提供します。

📖 [TeloPon 本体のドキュメントはこちら](https://github.com/miyumiyu/TeloPon)

---

## インストール方法

### 🔧 プラグインマネージャーから追加（推奨）

TeloPon 内の **「🔧 プラグイン管理」** →「ダウンロード可能」タブからワンクリックでインストールできます。

### 📁 手動でインストール

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
| 📺 | [YouTube Live+](docs/ja/YoutubeLiveOAuth.md) | 1.02 | YouTube OAuth連携。コメント読み書き・アンケート・タイトル変更・視聴者数取得。<br>👉 [詳細はこちら](docs/ja/YoutubeLiveOAuth.md) / [GCP設定ガイド](docs/ja/YoutubeLiveOAuth_GCP_Setup.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py) |
| 📺 | [ニコニコ生放送](docs/ja/NiconicoLivePlugin.md) | 1.00 | ニコニコ生放送のコメント・ギフト・広告・アンケート・統計をリアルタイム取得。運営コメント投稿も対応。<br>👉 [詳細はこちら](docs/ja/NiconicoLivePlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/NiconicoLivePlugin.py) |
| 🐦 | [X (Twitter)](docs/ja/XTwitterPlugin.md) | 1.11 | ハッシュタグ取得・サムネ/画面キャプチャ付きツイート投稿。有料API（Pay Per Use）。<br>👉 [詳細はこちら](docs/ja/XTwitterPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py) |
| 🔊 | [テロップ読み上げ (Windows)](docs/ja/WindowsTTS.md) | 1.00 | Windows標準音声（SAPI5）でテロップを自動読み上げ。<br>👉 [詳細はこちら](docs/ja/WindowsTTS.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py) |
| 🔊 | [テロップ読み上げ (VOICEVOX)](docs/ja/voicevox_plugin.md) | 1.00 | VOICEVOX音声合成でテロップを読み上げ。多数のキャラクターボイス対応。<br>👉 [詳細はこちら](docs/ja/voicevox_plugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py) |
| 📊 | [PowerPoint操作](docs/ja/PowerPointPlugin.md) | 1.00 | 音声指示でスライドショーを操作。ノートをAIに自動注入。<br>👉 [詳細はこちら](docs/ja/PowerPointPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/PowerPointPlugin.py) |
| 💬 | [Discord](docs/ja/discord_integration.md) | 1.00 | Discordチャンネルのコメントをリアルタイム取得。<br>👉 [詳細はこちら](docs/ja/discord_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py) |
| 💬 | [Slack](docs/ja/slack_integration.md) | 1.00 | Slackチャンネルのコメントをリアルタイム取得。<br>👉 [詳細はこちら](docs/ja/slack_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py) |
| 🎮 | [VCI テロップ送信](docs/ja/VciOscPlugin.md) | 1.01 | VirtualCast VCI へOSCでテロップ送信。<br>👉 [詳細はこちら](docs/ja/VciOscPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py) |

---

## プロンプト一覧

（準備中）

## テーマ一覧

（準備中）

---

## ライセンス

TeloPon 本体と同じライセンスに従います。

# 🐦 X (Twitter) Integration Plugin (XTwitterPlugin.py)

📥 **[Download XTwitterPlugin.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py)**

Fetches tweets by hashtag and injects them into the AI. AI can also auto-post tweets during the stream.

> **Note:** This plugin uses the paid X (Twitter) API. Registration at X Developer Portal and API billing are required.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| Hashtag Search | Periodically fetch tweets by hashtag and inject into AI |
| Tweet Posting | AI auto-posts tweets on streamer's command (with auto-hashtags) |

---

## ⚙️ Requirements

- X (Twitter) Developer Portal app (Read and Write permissions)
- Required library:

```
pip install tweepy
```

---

## 📋 Setup: Get API Keys from X Developer Portal

1. Visit [X Developer Portal](https://developer.x.com/) and sign in
2. Create a Project/App with **Read and Write** permissions
3. Generate and save these 4 keys:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret

---

## 📋 Plugin Configuration

1. Open the plugin settings from TeloPon's Extensions panel
2. Enter the 4 API keys and click **"Test Connection"**
3. Set the search hashtag and polling interval
4. Configure tweet posting options and default hashtags

---

## 🎤 Voice Commands

| Voice Command | Action |
|---|---|
| "Tweet this" / "Post to X" | AI composes and posts a tweet |
| "Tweet: hello world" | Posts the specified content |

---

## ⚠️ Notes

- **Paid API:** X API has no free tier. Pay-per-use billing required.
- **Polling interval:** Shorter intervals increase costs. 60+ seconds recommended.
- **Search limited to 7 days:** Only recent tweets are available.

---

[⬅️ Back to Extension Plugin List](../../README_en.md)

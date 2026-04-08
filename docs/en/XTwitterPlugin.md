# 🐦 X (Twitter) (XTwitterPlugin.py)

📥 **[Download XTwitterPlugin.py](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py)**

Fetches tweets by hashtag and injects them into the AI. AI can auto-post tweets with text, thumbnail images, or OBS screen captures.

> **Note:** This plugin uses the paid X (Twitter) API. Registration at X Developer Portal and Pay Per Use billing are required.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| Hashtag Search | Periodically fetch tweets by hashtag and inject into AI |
| Text Posting | AI auto-posts tweets with auto-appended hashtags and stream URL |
| Thumbnail Posting | Post tweets with the stream thumbnail image attached |
| Screen Capture Posting | Post tweets with OBS screen capture attached |

---

## ⚙️ Requirements

- X (Twitter) Developer Portal app (added to **Pay Per Use** package)
- Required library: `pip install tweepy`

---

## 📋 Setup

### 1. Get API Keys from X Developer Portal

1. Create an app at [X Developer Portal](https://developer.x.com/)
2. Set permissions to **Read and Write**
3. **Important:** Add the app to the "Pay Per Use" package (posting won't work with standalone apps)
4. Generate and save 4 keys: API Key, API Secret, Access Token, Access Token Secret
5. Add credits via Developer Portal billing

### 2. Plugin Configuration

1. Enter the 4 API keys and click **"Test Connection"**
2. Set the search hashtag and polling interval
3. Configure tweet posting options, default hashtags, and stream URL auto-attach
4. (Optional) Configure OBS WebSocket for screen capture tweets

---

## 🎤 Voice Commands

| Voice Command | Action |
|---|---|
| "Tweet this" / "Post to X" | Text-only tweet |
| "Tweet with thumbnail" | Tweet with stream thumbnail image |
| "Tweet with game screen" | Tweet with OBS screen capture |

---

## 💰 API Cost Estimate

| Operation | Cost | 2-hour stream estimate |
|---|---|---|
| Hashtag search | $0.005/request | ~$0.60 at 60s interval |
| Tweet posting | $0.01/tweet | ~$0.10 for 10 tweets |
| **Total** | | **~$0.70/stream (~100 JPY)** |

---

## ⚠️ Notes

- **Paid API:** X API has no free tier. Pay Per Use billing required.
- **Pay Per Use package:** App must be added to the package or posting returns 403.
- **Credit balance:** No credits = 402 error.
- **Polling interval:** Shorter intervals increase costs. 60+ seconds recommended.
- **Tweet length:** Keep text under 100 characters (URL and hashtags auto-appended).

---

[⬅️ Back to Extension Plugin List](../../README_en.md)

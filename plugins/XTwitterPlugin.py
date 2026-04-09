"""
XTwitterPlugin v1.00 - X (Twitter) 連携プラグイン

配信のハッシュタグでツイートを定期取得してAIに注入し、
AIが配信中にツイートを自動投稿できるプラグイン。

認証: OAuth 1.0a (API Key, API Secret, Access Token, Access Token Secret)
API: X API v2 (tweepy)

必要環境:
  - X Developer Portal のアプリ（読み取り+書き込み権限）
  - pip install tweepy
"""

import json
import os
import re
import threading
import time
import tkinter as tk
from tkinter import ttk

from plugin_manager import BasePlugin
import logger

_HAS_TWEEPY = True
try:
    import tweepy
except ImportError:
    _HAS_TWEEPY = False

# ==========================================
# 多言語対応
# ==========================================
_L = {
    "ja": {
        "plugin_name": "🐦 X (Twitter)",
        "window_title": "⚙️ X (Twitter) 連携 設定",
        "import_error": "tweepy がインストールされていません。\npip install tweepy を実行してください。",
        # 認証
        "section_auth": " 🔑 API認証設定 ",
        "btn_connect": "接続",
        "btn_disconnect": "切断",
        "lbl_auth_hint": "※ X Developer Portal でアプリを作成し、4つのキーを入力してください",
        "lbl_api_key": "API Key (Consumer Key):",
        "lbl_api_secret": "API Secret (Consumer Secret):",
        "lbl_access_token": "Access Token:",
        "lbl_access_secret": "Access Token Secret:",
        "btn_test_auth": "接続テスト",
        "btn_testing": "テスト中...",
        "auth_ok": "✅ 認証成功: @{screen_name}",
        "auth_fail": "❌ 認証失敗: {err}",
        "auth_none": "未認証",
        # ハッシュタグ
        "section_hashtag": " 🔍 ハッシュタグ取得 ",
        "lbl_hashtag": "検索ハッシュタグ:",
        "lbl_hashtag_hint": "例: TeloPon（#は不要）",
        "lbl_interval": "ポーリング間隔（秒）:",
        "chk_fetch_hashtag": "ハッシュタグのツイートを取得",
        # 投稿
        "section_post": " ✏️ ツイート投稿 ",
        "chk_ai_post": "AIによるツイート投稿",
        "chk_viewer_ok": "視聴者可",
        "lbl_default_hashtag": "投稿時の自動付与ハッシュタグ:",
        "lbl_default_hashtag_hint": "例: #TeloPon #配信（空欄なら付与しない）",
        "chk_attach_url": "配信URLを自動で付ける",
        # OBS
        "section_obs": " 📸 OBSキャプチャ（画像付きツイート用）",
        "lbl_obs_host": "OBS WebSocket Host:",
        "lbl_obs_port": "Port:",
        "lbl_obs_password": "Password:",
        "lbl_obs_source": "キャプチャソース名:",
        "btn_obs_test": "📸 テストキャプチャ",
        "obs_test_ok": "✅ キャプチャ成功",
        "obs_test_fail": "❌ キャプチャ失敗: {err}",
        # ボタン
        "btn_close": "閉じる",
        # AI注入
        "prompt_addon": (
            "# 【X (Twitter) 情報】\n"
            "あなたは X (Twitter) と連携しています。\n"
            "配信のハッシュタグ「#{hashtag}」のツイートが届くことがあります。\n"
        ),
        "prompt_cmd_post": (
            "\n# 【X (Twitter) 投稿コマンド】\n"
            "配信者の指示でツイートを投稿できます。テロップの末尾（[MEMO]の直前）に記述してください。\n"
            "* テキストのみ投稿: [CMD]X:post 100文字以内のツイート内容\n"
            "* サムネイル画像付き投稿: [CMD]X:post_thumb 100文字以内のツイート内容\n"
            "* ゲーム画面付き投稿: [CMD]X:post_screen 100文字以内のツイート内容\n"
            "\n## 配信者の発言に対する反応ルール\n"
            "* 「ツイートして」「Xに投稿して」→ [CMD]X:post 内容\n"
            "* 「サムネ付きでツイートして」「サムネイルを投稿して」→ [CMD]X:post_thumb 内容\n"
            "* 「ゲーム画面付きでツイートして」「画面を投稿して」→ [CMD]X:post_screen 内容\n"
            "\n## 重要\n"
            "* ツイートは100文字以内に収めてください（URL・ハッシュタグが自動付与されるため）\n"
            "* ハッシュタグ「{default_tags}」と配信URLは自動で付与されるため、本文に含めないでください\n"
            "\n## 視聴者コメントからの実行権限\n"
            "* 配信者の音声指示のみ（視聴者コメントでは実行禁止）\n"
        ),
        "tweet_cue": (
            "【番組ディレクターからのカンペ】\n"
            "X (Twitter) のハッシュタグ「#{hashtag}」に新しいツイートがあります:\n{tweets}\n"
            "盛り上がりに反応してください。"
        ),
        "post_ok_cue": "【カンペ】ツイート「{text}」を投稿しました。",
        "post_fail_cue": "【カンペ】ツイート投稿に失敗しました。",
        "video_capturing": "【カンペ】OBSリプレイバッファを保存しています...",
        "video_uploading": "【カンペ】動画をXにアップロードしています...",
        "video_ok_cue": "【カンペ】動画ツイート「{text}」を投稿しました。",
        "video_fail_cue": "【カンペ】動画ツイートに失敗しました: {err}",
        "prompt_cmd_video": (
            "* 動画付き投稿（直前の配信映像）: [CMD]X:post_video 100文字以内のツイート内容\n"
            "## 配信者の発言に対する反応ルール（追加）\n"
            "* 「動画送って」「Xに動画投稿して」「今のシーン送って」→ [CMD]X:post_video 内容\n"
        ),
    },
    "en": {
        "plugin_name": "🐦 X (Twitter)",
        "window_title": "⚙️ X (Twitter) Settings",
        "import_error": "tweepy is not installed.\nPlease run: pip install tweepy",
        "section_auth": " 🔑 API Authentication ",
        "btn_connect": "Connect",
        "btn_disconnect": "Disconnect",
        "lbl_auth_hint": "※ Create an app in X Developer Portal and enter the 4 keys",
        "lbl_api_key": "API Key (Consumer Key):",
        "lbl_api_secret": "API Secret (Consumer Secret):",
        "lbl_access_token": "Access Token:",
        "lbl_access_secret": "Access Token Secret:",
        "btn_test_auth": "Test Connection",
        "btn_testing": "Testing...",
        "auth_ok": "✅ Authenticated: @{screen_name}",
        "auth_fail": "❌ Auth failed: {err}",
        "auth_none": "Not authenticated",
        "section_hashtag": " 🔍 Hashtag Search ",
        "lbl_hashtag": "Search hashtag:",
        "lbl_hashtag_hint": "e.g. TeloPon (without #)",
        "lbl_interval": "Polling interval (sec):",
        "chk_fetch_hashtag": "Fetch hashtag tweets",
        "section_post": " ✏️ Tweet Posting ",
        "chk_ai_post": "AI tweet posting",
        "chk_viewer_ok": "Viewer OK",
        "lbl_default_hashtag": "Auto-append hashtags:",
        "lbl_default_hashtag_hint": "e.g. #TeloPon #streaming (empty = none)",
        "chk_attach_url": "Auto-attach stream URL",
        "section_obs": " 📸 OBS Capture (for image tweets)",
        "lbl_obs_host": "OBS WebSocket Host:",
        "lbl_obs_port": "Port:",
        "lbl_obs_password": "Password:",
        "lbl_obs_source": "Capture source name:",
        "btn_obs_test": "📸 Test Capture",
        "obs_test_ok": "✅ Capture OK",
        "obs_test_fail": "❌ Capture failed: {err}",
        "btn_close": "Close",
        "prompt_addon": (
            "# [X (Twitter) Info]\n"
            "You are connected to X (Twitter).\n"
            "Tweets with hashtag \"#{hashtag}\" may arrive.\n"
        ),
        "prompt_cmd_post": (
            "\n# [X (Twitter) Post Commands]\n"
            "* Text only: [CMD]X:post content (under 100 chars)\n"
            "* With thumbnail: [CMD]X:post_thumb content\n"
            "* With screen capture: [CMD]X:post_screen content\n"
        ),
        "tweet_cue": (
            "[Cue from Director]\n"
            "New tweets with hashtag \"#{hashtag}\":\n{tweets}\n"
            "React to the buzz."
        ),
        "post_ok_cue": "[Cue] Tweeted: \"{text}\"",
        "post_fail_cue": "[Cue] Tweet posting failed.",
        "video_capturing": "[Cue] Saving OBS replay buffer...",
        "video_uploading": "[Cue] Uploading video to X...",
        "video_ok_cue": "[Cue] Video tweeted: \"{text}\"",
        "video_fail_cue": "[Cue] Video tweet failed: {err}",
        "prompt_cmd_video": (
            "* With replay video: [CMD]X:post_video content (under 100 chars)\n"
            "* \"Send video\", \"Post video to X\", \"Post that scene\" → [CMD]X:post_video content\n"
        ),
    },
}


def _t(key: str, **kwargs) -> str:
    try:
        import i18n
        lang = i18n.get_lang()
    except Exception:
        lang = "en"
    text = _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


# ==========================================
# プラグイン本体
# ==========================================
_TAG = "[X/Twitter]"
_TOKEN_FILE = os.path.join("plugins", "twitter_x_token.json")


class XTwitterPlugin(BasePlugin):
    PLUGIN_ID = "twitter_x"
    PLUGIN_NAME = "X (Twitter) Integration"
    PLUGIN_VERSION = "1.00"
    PLUGIN_TYPE = "TOOL"

    IDENTIFIER = "X"  # [CMD]X:post

    def __init__(self):
        super().__init__()
        self.plugin_queue = None
        self.is_running = False
        self._live_queue = None
        self._live_prompt_config = None

        self._api = None  # tweepy.API (v1.1)
        self._auth_user = None  # screen_name
        self._api_authenticated = False  # API認証済みフラグ（切断ボタン以外では維持）
        self.is_connected = False  # コアUIバッジ用

        self._search_thread = None
        self._last_tweet_id = None

        self._panel = None

        # 起動時に4キーが揃っていれば自動接続
        self._try_auto_connect()

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "active": True,
            "api_key": "",
            "api_secret": "",
            "access_token": "",
            "access_secret": "",
            "hashtag": "",
            "poll_interval": 60,
            "fetch_hashtag": True,
            "ai_post": True,
            "viewer_post": False,
            "default_hashtags": "",
            "attach_stream_url": True,
            "obs_host": "127.0.0.1",
            "obs_port": 4455,
            "obs_password": "",
            "obs_source": "",
        }

    # ========================================
    # 認証
    # ========================================
    def _build_client(self):
        """tweepy API (v1.1) を構築。スタンドアロンアプリ（Project不要）で動作。"""
        if not _HAS_TWEEPY:
            return False
        settings = self.get_settings()
        api_key = settings.get("api_key", "")
        api_secret = settings.get("api_secret", "")
        access_token = settings.get("access_token", "")
        access_secret = settings.get("access_secret", "")
        if not all([api_key, api_secret, access_token, access_secret]):
            return False
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            self._api = tweepy.API(auth, wait_on_rate_limit=True)
            # 認証テスト
            me = self._api.verify_credentials()
            if me:
                self._auth_user = me.screen_name
                self._api_authenticated = True
                # 認証成功時に enabled も True にする
                settings["enabled"] = True
                self.save_settings(settings)
                logger.info(f"{_TAG} 認証成功: @{self._auth_user}")
                return True
            else:
                self._api = None
                return False
        except Exception as e:
            logger.warning(f"{_TAG} 認証失敗: {e}")
            self._api = None
            return False

    # ========================================
    # ライフサイクル
    # ========================================
    def get_prompt_addon(self):
        if not self._api_authenticated:
            return ""
        settings = self.get_settings()
        hashtag = settings.get("hashtag", "")
        parts = []
        if hashtag:
            parts.append(_t("prompt_addon", hashtag=hashtag))
        if settings.get("ai_post", True):
            default_tags = settings.get("default_hashtags", "")
            parts.append(_t("prompt_cmd_post", default_tags=default_tags))
            if settings.get("obs_host") and settings.get("obs_port"):
                parts.append(_t("prompt_cmd_video"))
        return "".join(parts)

    def start(self, prompt_config, plugin_queue):
        self._live_queue = plugin_queue
        self._live_prompt_config = prompt_config

        if not self._api_authenticated or not self._api:
            return

        self.cmt_msg = prompt_config.get("CMT_MSG", "")
        self.plugin_queue = plugin_queue
        self.is_running = True

        settings = self.get_settings()
        if settings.get("fetch_hashtag", True) and settings.get("hashtag", ""):
            self._search_thread = threading.Thread(target=self._search_loop, daemon=True)
            self._search_thread.start()

        logger.info(f"{_TAG} ▶️ ライブ連携開始")

    def stop(self):
        self.is_running = False
        self._live_queue = None
        self._live_prompt_config = None
        logger.info(f"{_TAG} ⏹️ ライブ連携停止")

    # ========================================
    # ハッシュタグ検索ループ
    # ========================================
    def _search_loop(self):
        """v1.1 API でハッシュタグ検索（スタンドアロンアプリ対応）"""
        settings = self.get_settings()
        hashtag = settings.get("hashtag", "").strip().lstrip("#")
        interval = max(30, settings.get("poll_interval", 60))

        if not hashtag:
            return

        query = f"#{hashtag} -filter:retweets"
        logger.info(f"{_TAG} ハッシュタグ検索開始: {query} (間隔: {interval}秒)")

        while self.is_running and self._api:
            try:
                kwargs = {
                    "q": query,
                    "count": 10,
                    "result_type": "recent",
                    "tweet_mode": "extended",
                }
                if self._last_tweet_id:
                    kwargs["since_id"] = int(self._last_tweet_id)

                results = self._api.search_tweets(**kwargs)

                if results:
                    tweets_text = []
                    for tweet in reversed(results):  # 古い順
                        name = f"@{tweet.user.screen_name}"
                        text = getattr(tweet, "full_text", tweet.text)[:100]
                        tweets_text.append(f"  {name}: {text}")
                        self._last_tweet_id = str(tweet.id)

                    if tweets_text and self.plugin_queue:
                        combined = "\n".join(tweets_text)
                        cue = _t("tweet_cue", hashtag=hashtag, tweets=combined)
                        self.send_text(self.plugin_queue, cue)
                        logger.info(f"{_TAG} {len(tweets_text)}件のツイートをAIに注入")

            except Exception as e:
                logger.warning(f"{_TAG} 検索エラー: {e}")

            time.sleep(interval)

    # ========================================
    # CMD ハンドラー: [CMD]X:post
    # ========================================
    def setup(self, cfg) -> bool:
        return True

    def handle(self, value: str):
        logger.info(f"{_TAG} [CMD]X: 受信 → '{value}'")
        if not value:
            logger.warning(f"{_TAG} [CMD]X: value が空のためスキップ")
            return
        if not self._api:
            logger.warning(f"{_TAG} [CMD]X: API未認証のためスキップ")
            return

        # 後続タグを除去
        value = re.sub(r'\[(?:WND|LAY|BDG|MEMO|TOPIC|MAIN)\].*$', '', value, flags=re.IGNORECASE).strip()
        if not value:
            logger.warning(f"{_TAG} [CMD]X: タグ除去後に空のためスキップ")
            return

        v_lower = value.lower()
        if v_lower.startswith("post_thumb"):
            text = value[10:].strip()
            if text:
                logger.info(f"{_TAG} [CMD]X:post_thumb → '{text[:50]}'")
                self._post_tweet(text, image_mode="thumbnail")
            else:
                logger.warning(f"{_TAG} [CMD]X:post_thumb テキストが空")
        elif v_lower.startswith("post_screen"):
            text = value[11:].strip()
            if text:
                logger.info(f"{_TAG} [CMD]X:post_screen → '{text[:50]}'")
                self._post_tweet(text, image_mode="screen")
            else:
                logger.warning(f"{_TAG} [CMD]X:post_screen テキストが空")
        elif v_lower.startswith("post_video"):
            text = value[10:].strip()
            if text:
                logger.info(f"{_TAG} [CMD]X:post_video → '{text[:50]}'")
                threading.Thread(target=self._post_video_tweet, args=(text,), daemon=True).start()
            else:
                logger.warning(f"{_TAG} [CMD]X:post_video テキストが空")
        elif v_lower.startswith("post"):
            text = value[4:].strip()
            if text:
                logger.info(f"{_TAG} [CMD]X:post → '{text[:50]}'")
                self._post_tweet(text)
            else:
                logger.warning(f"{_TAG} [CMD]X:post テキストが空")
        else:
            logger.warning(f"{_TAG} [CMD]X: 未知のサブコマンド '{value[:30]}'")

    def _post_tweet(self, text: str, image_mode: str = "none"):
        """ツイートを投稿
        image_mode: "none" / "thumbnail" / "screen"
        """
        if not self._api:
            return

        settings = self.get_settings()

        # ハッシュタグ付与
        default_tags = settings.get("default_hashtags", "").strip()
        if default_tags:
            text = f"{text} {default_tags}"

        # 配信URL付与
        if settings.get("attach_stream_url", True):
            stream_url = self.get_stream_url()
            if stream_url:
                text = f"{text}\n{stream_url}"

        # 280文字制限
        if len(text) > 280:
            text = text[:277] + "..."

        try:
            media_id = None

            # 画像添付
            if image_mode == "thumbnail":
                media_id = self._upload_thumbnail()
            elif image_mode == "screen":
                media_id = self._upload_obs_screenshot()

            # v2 Client で投稿
            client_v2 = tweepy.Client(
                consumer_key=settings.get("api_key", ""),
                consumer_secret=settings.get("api_secret", ""),
                access_token=settings.get("access_token", ""),
                access_token_secret=settings.get("access_secret", ""),
            )
            kwargs = {"text": text}
            if media_id:
                kwargs["media_ids"] = [media_id]
            client_v2.create_tweet(**kwargs)
            logger.info(f"{_TAG} ツイート投稿: {text[:50]} (image={image_mode})")
            if self.plugin_queue:
                self.send_text(self.plugin_queue, _t("post_ok_cue", text=text[:50]))
        except Exception as e:
            logger.warning(f"{_TAG} ツイート投稿エラー: {e}")
            if self.plugin_queue:
                self.send_text(self.plugin_queue, _t("post_fail_cue"))

    def _upload_thumbnail(self) -> str | None:
        """コア共有機構からサムネイル画像を取得してアップロード（v1.1 media_upload）"""
        thumb_bytes, mime = self.get_stream_thumbnail()
        if not thumb_bytes:
            logger.warning(f"{_TAG} サムネイル画像がありません")
            return None
        return self._upload_image_bytes(thumb_bytes, mime)

    def _upload_obs_screenshot(self) -> str | None:
        """OBS WebSocket でスクリーンショットを取得してアップロード"""
        try:
            import base64
            import obsws_python as obs

            settings = self.get_settings()
            host = settings.get("obs_host", "127.0.0.1")
            port = int(settings.get("obs_port", 4455))
            password = settings.get("obs_password", "")
            source = settings.get("obs_source", "")
            if not source:
                logger.warning(f"{_TAG} OBSキャプチャソース名が未設定")
                return None

            cl = obs.ReqClient(host=host, port=port, password=password, timeout=3)
            res = cl.get_source_screenshot(source, "jpeg", 1280, 720, 80)
            img_data = res.image_data
            if img_data.startswith("data:image/jpeg;base64,"):
                img_data = img_data.replace("data:image/jpeg;base64,", "")
            img_bytes = base64.b64decode(img_data)
            logger.info(f"{_TAG} OBSキャプチャ取得: {len(img_bytes)} bytes")
            return self._upload_image_bytes(img_bytes, "image/jpeg")
        except Exception as e:
            logger.warning(f"{_TAG} OBSキャプチャエラー: {e}")
            return None

    def _upload_image_bytes(self, img_bytes: bytes, mime_type: str = "image/jpeg") -> str | None:
        """画像バイトを v1.1 media_upload でアップロードし media_id を返す"""
        try:
            import io
            import tempfile
            ext = ".jpg" if "jpeg" in mime_type else ".png"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            try:
                media = self._api.media_upload(filename=tmp_path)
                logger.info(f"{_TAG} 画像アップロード成功: media_id={media.media_id}")
                return str(media.media_id)
            finally:
                import os as _os
                _os.unlink(tmp_path)
        except Exception as e:
            logger.warning(f"{_TAG} 画像アップロードエラー: {e}")
            return None

    def _post_video_tweet(self, text: str):
        """動画付きツイートを投稿（OBSリプレイバッファ → Xアップロード → ツイート）"""
        if not self._api:
            return

        def _cue(msg):
            if self.plugin_queue:
                self.send_text(self.plugin_queue, msg)

        _cue(_t("video_capturing"))

        video_path = self._capture_replay_video()
        if not video_path:
            _cue(_t("video_fail_cue", err="リプレイバッファ保存失敗"))
            return

        _cue(_t("video_uploading"))

        media_id = self._upload_video(video_path)
        if not media_id:
            _cue(_t("video_fail_cue", err="動画アップロード失敗"))
            return

        settings = self.get_settings()
        default_tags = settings.get("default_hashtags", "").strip()
        if default_tags:
            text = f"{text} {default_tags}"
        if settings.get("attach_stream_url", True):
            stream_url = self.get_stream_url()
            if stream_url:
                text = f"{text}\n{stream_url}"
        if len(text) > 280:
            text = text[:277] + "..."

        try:
            client_v2 = tweepy.Client(
                consumer_key=settings.get("api_key", ""),
                consumer_secret=settings.get("api_secret", ""),
                access_token=settings.get("access_token", ""),
                access_token_secret=settings.get("access_secret", ""),
            )
            client_v2.create_tweet(text=text, media_ids=[media_id])
            logger.info(f"{_TAG} 動画ツイート投稿成功: {text[:50]}")
            _cue(_t("video_ok_cue", text=text[:50]))
        except Exception as e:
            logger.warning(f"{_TAG} 動画ツイート投稿エラー: {e}")
            _cue(_t("video_fail_cue", err=str(e)[:60]))

    def _capture_replay_video(self) -> str | None:
        """OBSリプレイバッファを保存してファイルパスを返す。
        EventClient で ReplayBufferSaved イベントを受け取りパスを自動取得。
        """
        try:
            import obsws_python as obs

            settings = self.get_settings()
            host = settings.get("obs_host", "127.0.0.1")
            port = int(settings.get("obs_port", 4455))
            password = settings.get("obs_password", "")

            saved_path: list[str | None] = [None]
            path_event = threading.Event()

            ev_client = obs.EventClient(host=host, port=port, password=password)

            def on_replay_buffer_saved(data):
                saved_path[0] = getattr(data, "saved_replay_path", None)
                path_event.set()

            ev_client.callback.register(on_replay_buffer_saved)

            req_client = obs.ReqClient(host=host, port=port, password=password, timeout=5)
            req_client.save_replay_buffer()
            logger.info(f"{_TAG} SaveReplayBuffer 送信")

            path_event.wait(timeout=15)
            try:
                ev_client.disconnect()
            except Exception:
                pass

            if saved_path[0]:
                logger.info(f"{_TAG} リプレイバッファ保存完了: {saved_path[0]}")
                return saved_path[0]
            else:
                logger.warning(f"{_TAG} リプレイバッファ保存タイムアウト")
                return None
        except Exception as e:
            logger.warning(f"{_TAG} _capture_replay_video エラー: {e}")
            return None

    def _upload_video(self, video_path: str) -> str | None:
        """動画ファイルを v1.1 chunked media_upload でアップロードし media_id を返す。
        アップロード後、Xサーバー側の処理完了をポーリングで待つ。
        """
        try:
            import time as _time

            media = self._api.media_upload(
                filename=video_path,
                media_category="tweet_video",
                chunked=True,
            )
            media_id = media.media_id
            logger.info(f"{_TAG} 動画アップロード開始: media_id={media_id}")

            for _ in range(60):  # 最大120秒
                status = self._api.get_media_upload_status(media_id)
                info = getattr(status, "processing_info", None)
                if info is None:
                    break
                state = info.get("state", "")
                if state == "succeeded":
                    logger.info(f"{_TAG} 動画処理完了: media_id={media_id}")
                    break
                elif state == "failed":
                    err = info.get("error", {}).get("message", "unknown")
                    logger.warning(f"{_TAG} 動画処理失敗: {err}")
                    return None
                _time.sleep(info.get("check_after_secs", 2))

            return str(media_id)
        except Exception as e:
            logger.warning(f"{_TAG} _upload_video エラー: {e}")
            return None

    # ========================================
    # 設定UI
    # ========================================
    def open_settings_ui(self, parent_window):
        if not _HAS_TWEEPY:
            from tkinter import messagebox
            messagebox.showerror("Error", _t("import_error"))
            return

        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("window_title"))
        self._panel.geometry("480x700")
        self._panel.minsize(460, 660)
        self._panel.attributes("-topmost", True)

        main_f = ttk.Frame(self._panel, padding=10)
        main_f.pack(fill=tk.BOTH, expand=True)

        settings = self.get_settings()

        # --- 認証セクション ---
        auth_f = ttk.LabelFrame(main_f, text=_t("section_auth"), padding=8)
        auth_f.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(auth_f, text=_t("lbl_auth_hint"), foreground="gray", font=("", 8)).pack(anchor="w", pady=(0, 4))

        ttk.Label(auth_f, text=_t("lbl_api_key"), font=("", 8)).pack(anchor="w")
        self._ent_api_key = ttk.Entry(auth_f, font=("", 9), show="*")
        self._ent_api_key.pack(fill=tk.X, pady=(0, 2))
        self._ent_api_key.insert(0, settings.get("api_key", ""))

        ttk.Label(auth_f, text=_t("lbl_api_secret"), font=("", 8)).pack(anchor="w")
        self._ent_api_secret = ttk.Entry(auth_f, font=("", 9), show="*")
        self._ent_api_secret.pack(fill=tk.X, pady=(0, 2))
        self._ent_api_secret.insert(0, settings.get("api_secret", ""))

        ttk.Label(auth_f, text=_t("lbl_access_token"), font=("", 8)).pack(anchor="w")
        self._ent_access_token = ttk.Entry(auth_f, font=("", 9), show="*")
        self._ent_access_token.pack(fill=tk.X, pady=(0, 2))
        self._ent_access_token.insert(0, settings.get("access_token", ""))

        ttk.Label(auth_f, text=_t("lbl_access_secret"), font=("", 8)).pack(anchor="w")
        self._ent_access_secret = ttk.Entry(auth_f, font=("", 9), show="*")
        self._ent_access_secret.pack(fill=tk.X, pady=(0, 2))
        self._ent_access_secret.insert(0, settings.get("access_secret", ""))

        btn_f = ttk.Frame(auth_f)
        btn_f.pack(fill=tk.X, pady=(4, 0))
        if self._api_authenticated:
            self._btn_connect = tk.Button(
                btn_f, text=_t("btn_disconnect"), bg="#dc3545", fg="white",
                font=("", 9, "bold"), command=self._on_disconnect,
            )
        else:
            self._btn_connect = tk.Button(
                btn_f, text=_t("btn_connect"), bg="#1DA1F2", fg="white",
                font=("", 9, "bold"), command=self._on_test_auth,
            )
        self._btn_connect.pack(side="left")
        self._lbl_auth_status = ttk.Label(
            btn_f, text=_t("auth_ok", screen_name=self._auth_user) if self._api_authenticated else _t("auth_none"),
            foreground="green" if self._api_authenticated else "gray", font=("", 8),
        )
        self._lbl_auth_status.pack(side="left", padx=(8, 0))

        # --- ハッシュタグセクション ---
        self._hash_f = ttk.LabelFrame(main_f, text=_t("section_hashtag"), padding=8)
        self._hash_f.pack(fill=tk.X, pady=(0, 8))
        hash_f = self._hash_f

        self._var_fetch = tk.BooleanVar(value=settings.get("fetch_hashtag", True))
        ttk.Checkbutton(hash_f, text=_t("chk_fetch_hashtag"), variable=self._var_fetch,
                        command=self._update_badge).pack(anchor="w")

        ht_f = ttk.Frame(hash_f)
        ht_f.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(ht_f, text=_t("lbl_hashtag"), font=("", 8)).pack(side="left")
        self._ent_hashtag = ttk.Entry(ht_f, font=("", 9), width=20)
        self._ent_hashtag.pack(side="left", padx=(4, 8))
        self._ent_hashtag.insert(0, settings.get("hashtag", ""))
        ttk.Label(ht_f, text=_t("lbl_hashtag_hint"), foreground="gray", font=("", 7)).pack(side="left")

        int_f = ttk.Frame(hash_f)
        int_f.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(int_f, text=_t("lbl_interval"), font=("", 8)).pack(side="left")
        self._var_interval = tk.IntVar(value=settings.get("poll_interval", 60))
        ttk.Spinbox(int_f, from_=30, to=300, increment=10, textvariable=self._var_interval,
                     width=6, font=("", 9)).pack(side="left", padx=(4, 0))

        # --- 投稿セクション ---
        self._post_f = ttk.LabelFrame(main_f, text=_t("section_post"), padding=8)
        self._post_f.pack(fill=tk.X, pady=(0, 8))
        post_f = self._post_f

        row_f = ttk.Frame(post_f)
        row_f.pack(fill=tk.X)
        self._var_ai_post = tk.BooleanVar(value=settings.get("ai_post", True))
        ttk.Checkbutton(row_f, text=_t("chk_ai_post"), variable=self._var_ai_post,
                        command=self._update_badge).pack(side="left")
        self._var_viewer_post = tk.BooleanVar(value=settings.get("viewer_post", False))
        ttk.Label(row_f, text=_t("chk_viewer_ok"), font=("", 7), foreground="gray").pack(side="left", padx=(12, 0))
        ttk.Checkbutton(row_f, variable=self._var_viewer_post).pack(side="left")

        ttk.Label(post_f, text=_t("lbl_default_hashtag"), font=("", 8)).pack(anchor="w", pady=(4, 0))
        self._ent_default_tags = ttk.Entry(post_f, font=("", 9))
        self._ent_default_tags.pack(fill=tk.X, pady=(0, 2))
        self._ent_default_tags.insert(0, settings.get("default_hashtags", ""))
        ttk.Label(post_f, text=_t("lbl_default_hashtag_hint"), foreground="gray", font=("", 7)).pack(anchor="w")

        self._var_attach_url = tk.BooleanVar(value=settings.get("attach_stream_url", True))
        ttk.Checkbutton(post_f, text=_t("chk_attach_url"), variable=self._var_attach_url).pack(anchor="w", pady=(4, 0))

        # --- OBSキャプチャセクション（2カラム）---
        self._obs_f = ttk.LabelFrame(main_f, text=_t("section_obs"), padding=8)
        self._obs_f.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        obs_f = self._obs_f

        obs_cols = ttk.Frame(obs_f)
        obs_cols.pack(fill=tk.BOTH, expand=True)

        # 左カラム: 設定項目
        obs_left = ttk.Frame(obs_cols)
        obs_left.pack(side="left", fill=tk.BOTH, expand=True, padx=(0, 6))

        obs_row1 = ttk.Frame(obs_left)
        obs_row1.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(obs_row1, text=_t("lbl_obs_host"), font=("", 8)).pack(anchor="w")
        host_port_f = ttk.Frame(obs_row1)
        host_port_f.pack(fill=tk.X)
        self._ent_obs_host = ttk.Entry(host_port_f, font=("", 9), width=12)
        self._ent_obs_host.pack(side="left")
        self._ent_obs_host.insert(0, settings.get("obs_host", "127.0.0.1"))
        ttk.Label(host_port_f, text=":", font=("", 8)).pack(side="left")
        self._ent_obs_port = ttk.Entry(host_port_f, font=("", 9), width=5)
        self._ent_obs_port.pack(side="left")
        self._ent_obs_port.insert(0, str(settings.get("obs_port", 4455)))

        ttk.Label(obs_left, text=_t("lbl_obs_password"), font=("", 8)).pack(anchor="w", pady=(2, 0))
        self._ent_obs_password = ttk.Entry(obs_left, font=("", 9), show="*")
        self._ent_obs_password.pack(fill=tk.X, pady=(0, 2))
        self._ent_obs_password.insert(0, settings.get("obs_password", ""))

        ttk.Label(obs_left, text=_t("lbl_obs_source"), font=("", 8)).pack(anchor="w", pady=(2, 0))
        self._combo_obs_source = ttk.Combobox(obs_left, font=("", 9), state="readonly")
        self._combo_obs_source.pack(fill=tk.X, pady=(0, 4))
        self._combo_obs_source.set(settings.get("obs_source", ""))
        self._combo_obs_source.bind("<Button-1>", lambda e: self._fetch_obs_scenes())

        obs_btn_f = ttk.Frame(obs_left)
        obs_btn_f.pack(fill=tk.X)
        tk.Button(
            obs_btn_f, text=_t("btn_obs_test"), font=("", 8),
            bg="#17a2b8", fg="white", command=self._on_obs_test,
        ).pack(side="left")
        self._lbl_obs_status = ttk.Label(obs_btn_f, text="", font=("", 7))
        self._lbl_obs_status.pack(side="left", padx=(6, 0))

        # 右カラム: プレビュー画像（16:9）
        obs_right = ttk.Frame(obs_cols, width=192, height=108)
        obs_right.pack(side="right", fill=tk.NONE, anchor="n")
        obs_right.pack_propagate(False)
        self._lbl_obs_preview = ttk.Label(obs_right, text="[ Preview ]", anchor="center",
                                           background="#222", foreground="#666", font=("", 8))
        self._lbl_obs_preview.pack(fill=tk.BOTH, expand=True)
        self._obs_preview_photo = None

        # 起動時にシーン一覧を取得
        self._fetch_obs_scenes()

        # --- 閉じるボタン ---
        tk.Button(
            main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
            font=("", 10, "bold"), command=self._save_and_close,
        ).pack(fill=tk.X, pady=(8, 0))
        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

        # 認証状態に応じて機能セクションをグレーアウト
        self._update_feature_state()

    def _fetch_obs_scenes(self):
        """OBSからシーン一覧を取得してコンボボックスに設定"""
        def _do():
            try:
                import obsws_python as obs_ws
                host = self._ent_obs_host.get().strip()
                port = int(self._ent_obs_port.get().strip() or 4455)
                password = self._ent_obs_password.get().strip()
                cl = obs_ws.ReqClient(host=host, port=port, password=password, timeout=3)
                scenes = cl.get_scene_list()
                scene_names = []
                if scenes and hasattr(scenes, 'scenes'):
                    for scene in scenes.scenes:
                        name = scene.get("sceneName", "") if isinstance(scene, dict) else getattr(scene, "sceneName", "")
                        if name:
                            scene_names.append(name)
                if scene_names and self._panel and self._panel.winfo_exists():
                    self._panel.after(0, lambda names=scene_names: self._combo_obs_source.config(values=names))
            except Exception:
                pass
        threading.Thread(target=_do, daemon=True).start()

    def _on_obs_test(self):
        """OBSキャプチャのテスト — プレビュー画像を表示"""
        self._lbl_obs_status.config(text="...", foreground="orange")

        def _do():
            try:
                import base64
                import io
                import obsws_python as obs
                from PIL import Image, ImageTk

                host = self._ent_obs_host.get().strip()
                port = int(self._ent_obs_port.get().strip() or 4455)
                password = self._ent_obs_password.get().strip()
                source = self._combo_obs_source.get().strip()
                if not source:
                    if self._panel and self._panel.winfo_exists():
                        self._panel.after(0, lambda: self._lbl_obs_status.config(
                            text=_t("obs_test_fail", err="Source name empty"), foreground="red"))
                    return

                cl = obs.ReqClient(host=host, port=port, password=password, timeout=3)
                res = cl.get_source_screenshot(source, "jpeg", 1280, 720, 80)
                img_data = res.image_data
                if img_data.startswith("data:image/jpeg;base64,"):
                    img_data = img_data.replace("data:image/jpeg;base64,", "")
                img_bytes = base64.b64decode(img_data)

                # プレビュー画像を表示
                img = Image.open(io.BytesIO(img_bytes))
                img.thumbnail((192, 108))
                if self._panel and self._panel.winfo_exists():
                    def _show():
                        self._obs_preview_photo = ImageTk.PhotoImage(img)
                        self._lbl_obs_preview.config(image=self._obs_preview_photo, text="")
                        self._lbl_obs_status.config(text=_t("obs_test_ok"), foreground="green")
                    self._panel.after(0, _show)
                logger.info(f"{_TAG} OBSテストキャプチャ成功: {len(img_bytes)} bytes")
            except Exception as e:
                logger.warning(f"{_TAG} OBSテストキャプチャ失敗: {e}")
                if self._panel and self._panel.winfo_exists():
                    self._panel.after(0, lambda: self._lbl_obs_status.config(
                        text=_t("obs_test_fail", err=str(e)[:40]), foreground="red"))

        threading.Thread(target=_do, daemon=True).start()

    def _try_auto_connect(self):
        """起動時に4キーが揃っていれば自動で接続"""
        if not _HAS_TWEEPY:
            return
        settings = self.get_settings()
        keys = [settings.get(k, "") for k in ("api_key", "api_secret", "access_token", "access_secret")]
        if all(keys):
            if self._build_client():
                self._api_authenticated = True
                self._update_badge_from_settings()
                logger.info(f"{_TAG} 起動時自動接続成功: @{self._auth_user}")

    def _update_badge(self):
        """コアUIのバッジ表示を更新: 認証済 AND (取得チェック or 投稿チェック) でアクティブ"""
        if self._api_authenticated:
            fetch = self._var_fetch.get() if hasattr(self, '_var_fetch') else False
            post = self._var_ai_post.get() if hasattr(self, '_var_ai_post') else False
            self.is_connected = fetch or post
        else:
            self.is_connected = False

    def _update_badge_from_settings(self):
        """UIが開いていない時（起動時等）に設定JSONからバッジを更新"""
        if self._api_authenticated:
            settings = self.get_settings()
            fetch = settings.get("fetch_hashtag", True)
            post = settings.get("ai_post", True)
            self.is_connected = fetch or post
        else:
            self.is_connected = False

    def _update_feature_state(self):
        """認証状態に応じて機能セクションを有効/無効切替（再帰的に全子ウィジェット）"""
        enabled = self._api_authenticated
        for frame in [self._hash_f, self._post_f, self._obs_f]:
            if hasattr(self, '_panel') and frame.winfo_exists():
                self._set_widget_state_recursive(frame, enabled)

    @staticmethod
    def _set_widget_state_recursive(widget, enabled):
        """ウィジェットとその全子要素の状態を再帰的に設定"""
        for child in widget.winfo_children():
            # 再帰
            XTwitterPlugin._set_widget_state_recursive(child, enabled)
            # ttk系
            try:
                child.state(["!disabled"] if enabled else ["disabled"])
                continue
            except (AttributeError, tk.TclError):
                pass
            # tk系
            try:
                child.config(state="normal" if enabled else "disabled")
            except (AttributeError, tk.TclError):
                pass

    def _on_disconnect(self):
        """切断"""
        self._api = None
        self._auth_user = None
        self._api_authenticated = False
        self.is_connected = False
        settings = self.get_settings()
        settings["enabled"] = False
        self.save_settings(settings)
        if hasattr(self, '_btn_connect'):
            self._btn_connect.config(
                state="normal", text=_t("btn_connect"), bg="#1DA1F2",
                command=self._on_test_auth,
            )
        if hasattr(self, '_lbl_auth_status'):
            self._lbl_auth_status.config(text=_t("auth_none"), foreground="gray")
        self._update_feature_state()
        logger.info(f"{_TAG} 切断しました")

    def _on_test_auth(self):
        """接続"""
        self._save_keys()
        self._btn_connect.config(state="disabled", text=_t("btn_testing"))
        self._lbl_auth_status.config(text=_t("btn_testing"), foreground="orange")

        def _do():
            ok = self._build_client()
            if self._panel and self._panel.winfo_exists():
                if ok:
                    self._panel.after(0, self._on_connect_success)
                else:
                    self._panel.after(0, self._on_connect_fail)

        threading.Thread(target=_do, daemon=True).start()

    def _on_connect_success(self):
        self._btn_connect.config(
            state="normal", text=_t("btn_disconnect"), bg="#dc3545",
            command=self._on_disconnect,
        )
        self._lbl_auth_status.config(
            text=_t("auth_ok", screen_name=self._auth_user), foreground="green",
        )
        self._update_feature_state()
        self._update_badge()

    def _on_connect_fail(self):
        self._btn_connect.config(
            state="normal", text=_t("btn_connect"), bg="#1DA1F2",
            command=self._on_test_auth,
        )
        self._lbl_auth_status.config(
            text=_t("auth_fail", err="Invalid credentials"), foreground="red",
        )

    def _save_keys(self):
        """キー入力をsettingsに保存"""
        settings = self.get_settings()
        settings["api_key"] = self._ent_api_key.get().strip()
        settings["api_secret"] = self._ent_api_secret.get().strip()
        settings["access_token"] = self._ent_access_token.get().strip()
        settings["access_secret"] = self._ent_access_secret.get().strip()
        self.save_settings(settings)

    def _save_and_close(self):
        settings = self.get_settings()
        settings["api_key"] = self._ent_api_key.get().strip()
        settings["api_secret"] = self._ent_api_secret.get().strip()
        settings["access_token"] = self._ent_access_token.get().strip()
        settings["access_secret"] = self._ent_access_secret.get().strip()
        settings["hashtag"] = self._ent_hashtag.get().strip().lstrip("#")
        settings["poll_interval"] = self._var_interval.get()
        settings["fetch_hashtag"] = self._var_fetch.get()
        settings["ai_post"] = self._var_ai_post.get()
        settings["viewer_post"] = self._var_viewer_post.get()
        settings["default_hashtags"] = self._ent_default_tags.get().strip()
        settings["attach_stream_url"] = self._var_attach_url.get()
        settings["obs_host"] = self._ent_obs_host.get().strip()
        settings["obs_port"] = int(self._ent_obs_port.get().strip() or 4455)
        settings["obs_password"] = self._ent_obs_password.get().strip()
        settings["obs_source"] = self._combo_obs_source.get().strip()
        self.save_settings(settings)
        self._panel.destroy()

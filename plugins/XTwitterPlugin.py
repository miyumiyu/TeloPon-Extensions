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
        "plugin_name": "X (Twitter) 連携",
        "window_title": "⚙️ X (Twitter) 連携 設定",
        "import_error": "tweepy がインストールされていません。\npip install tweepy を実行してください。",
        # 認証
        "section_auth": " 🔑 API認証設定 ",
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
            "* ツイート投稿: [CMD]X:post ツイート内容\n"
            "\n## 配信者の発言に対する反応ルール\n"
            "* 「ツイートして」「Xに投稿して」→ 内容を考えて [CMD]X:post 投稿内容\n"
            "* 「○○ってツイートして」→ [CMD]X:post ○○\n"
            "\n## 重要\n"
            "* ツイートは140文字以内に収めてください\n"
            "* ハッシュタグ「{default_tags}」は自動で付与されるため、本文に含めないでください\n"
            "* 投稿コマンド実行時はテロップ（[MAIN]）を「スキップ」にしてください\n"
            "  例: [MAIN]スキップ[CMD]X:post 配信中です！[MEMO]ツイート\n"
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
    },
    "en": {
        "plugin_name": "X (Twitter) Integration",
        "window_title": "⚙️ X (Twitter) Settings",
        "import_error": "tweepy is not installed.\nPlease run: pip install tweepy",
        "section_auth": " 🔑 API Authentication ",
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
        "btn_close": "Close",
        "prompt_addon": (
            "# [X (Twitter) Info]\n"
            "You are connected to X (Twitter).\n"
            "Tweets with hashtag \"#{hashtag}\" may arrive.\n"
        ),
        "prompt_cmd_post": (
            "\n# [X (Twitter) Post Commands]\n"
            "You can post tweets on the streamer's instruction.\n"
            "* Post tweet: [CMD]X:post tweet content\n"
            "\n## Important\n"
            "* Keep tweets under 280 characters\n"
            "* Hashtags \"{default_tags}\" are auto-appended\n"
            "* Use [MAIN]スキップ when posting\n"
        ),
        "tweet_cue": (
            "[Cue from Director]\n"
            "New tweets with hashtag \"#{hashtag}\":\n{tweets}\n"
            "React to the buzz."
        ),
        "post_ok_cue": "[Cue] Tweeted: \"{text}\"",
        "post_fail_cue": "[Cue] Tweet posting failed.",
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

        self._client = None  # tweepy.Client
        self._auth_user = None  # screen_name
        self.is_connected = False

        self._search_thread = None
        self._last_tweet_id = None

        self._panel = None

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
        }

    # ========================================
    # 認証
    # ========================================
    def _build_client(self):
        """tweepy Client を構築"""
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
            self._client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
                wait_on_rate_limit=True,
            )
            # 認証テスト
            me = self._client.get_me()
            if me and me.data:
                self._auth_user = me.data.username
                self.is_connected = True
                logger.info(f"{_TAG} 認証成功: @{self._auth_user}")
                return True
            else:
                self._client = None
                return False
        except Exception as e:
            logger.warning(f"{_TAG} 認証失敗: {e}")
            self._client = None
            return False

    # ========================================
    # ライフサイクル
    # ========================================
    def get_prompt_addon(self):
        if not self.is_connected:
            return ""
        settings = self.get_settings()
        hashtag = settings.get("hashtag", "")
        parts = []
        if hashtag:
            parts.append(_t("prompt_addon", hashtag=hashtag))
        if settings.get("ai_post", True):
            default_tags = settings.get("default_hashtags", "")
            parts.append(_t("prompt_cmd_post", default_tags=default_tags))
        return "".join(parts)

    def start(self, prompt_config, plugin_queue):
        self._live_queue = plugin_queue
        self._live_prompt_config = prompt_config

        if not self.is_connected or not self._client:
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
        settings = self.get_settings()
        hashtag = settings.get("hashtag", "").strip().lstrip("#")
        interval = max(30, settings.get("poll_interval", 60))

        if not hashtag:
            return

        query = f"#{hashtag} -is:retweet"
        logger.info(f"{_TAG} ハッシュタグ検索開始: {query} (間隔: {interval}秒)")

        while self.is_running and self._client:
            try:
                kwargs = {
                    "query": query,
                    "max_results": 10,
                    "tweet_fields": ["author_id", "created_at"],
                    "expansions": ["author_id"],
                    "user_fields": ["username", "name", "profile_image_url"],
                }
                if self._last_tweet_id:
                    kwargs["since_id"] = self._last_tweet_id

                resp = self._client.search_recent_tweets(**kwargs)

                if resp and resp.data:
                    # ユーザー名マップ作成
                    user_map = {}
                    if resp.includes and "users" in resp.includes:
                        for u in resp.includes["users"]:
                            user_map[u.id] = u

                    tweets_text = []
                    for tweet in reversed(resp.data):  # 古い順
                        user = user_map.get(tweet.author_id)
                        name = f"@{user.username}" if user else "unknown"
                        tweets_text.append(f"  {name}: {tweet.text[:100]}")
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
        if not value or not self._client:
            return

        # 後続タグを除去
        value = re.sub(r'\[(?:WND|LAY|BDG|MEMO|TOPIC|MAIN)\].*$', '', value, flags=re.IGNORECASE).strip()
        if not value:
            return

        v_lower = value.lower()
        if v_lower.startswith("post"):
            text = value[4:].strip()
            if text:
                self._post_tweet(text)

    def _post_tweet(self, text: str):
        """ツイートを投稿"""
        if not self._client:
            return

        settings = self.get_settings()
        default_tags = settings.get("default_hashtags", "").strip()
        if default_tags:
            text = f"{text} {default_tags}"

        # 280文字制限
        if len(text) > 280:
            text = text[:277] + "..."

        try:
            self._client.create_tweet(text=text)
            logger.info(f"{_TAG} ツイート投稿: {text[:50]}")
            if self.plugin_queue:
                self.send_text(self.plugin_queue, _t("post_ok_cue", text=text[:50]))
        except Exception as e:
            logger.warning(f"{_TAG} ツイート投稿エラー: {e}")
            if self.plugin_queue:
                self.send_text(self.plugin_queue, _t("post_fail_cue"))

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
        self._panel.geometry("480x560")
        self._panel.minsize(460, 520)
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

        test_f = ttk.Frame(auth_f)
        test_f.pack(fill=tk.X, pady=(4, 0))
        self._btn_test = tk.Button(
            test_f, text=_t("btn_test_auth"), bg="#1DA1F2", fg="white",
            font=("", 9, "bold"), command=self._on_test_auth,
        )
        self._btn_test.pack(side="left")
        self._lbl_auth_status = ttk.Label(
            test_f, text=_t("auth_ok", screen_name=self._auth_user) if self.is_connected else _t("auth_none"),
            foreground="green" if self.is_connected else "gray", font=("", 8),
        )
        self._lbl_auth_status.pack(side="left", padx=(8, 0))

        # --- ハッシュタグセクション ---
        hash_f = ttk.LabelFrame(main_f, text=_t("section_hashtag"), padding=8)
        hash_f.pack(fill=tk.X, pady=(0, 8))

        self._var_fetch = tk.BooleanVar(value=settings.get("fetch_hashtag", True))
        ttk.Checkbutton(hash_f, text=_t("chk_fetch_hashtag"), variable=self._var_fetch).pack(anchor="w")

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
        post_f = ttk.LabelFrame(main_f, text=_t("section_post"), padding=8)
        post_f.pack(fill=tk.X, pady=(0, 8))

        row_f = ttk.Frame(post_f)
        row_f.pack(fill=tk.X)
        self._var_ai_post = tk.BooleanVar(value=settings.get("ai_post", True))
        ttk.Checkbutton(row_f, text=_t("chk_ai_post"), variable=self._var_ai_post).pack(side="left")
        self._var_viewer_post = tk.BooleanVar(value=settings.get("viewer_post", False))
        ttk.Label(row_f, text=_t("chk_viewer_ok"), font=("", 7), foreground="gray").pack(side="left", padx=(12, 0))
        ttk.Checkbutton(row_f, variable=self._var_viewer_post).pack(side="left")

        ttk.Label(post_f, text=_t("lbl_default_hashtag"), font=("", 8)).pack(anchor="w", pady=(4, 0))
        self._ent_default_tags = ttk.Entry(post_f, font=("", 9))
        self._ent_default_tags.pack(fill=tk.X, pady=(0, 2))
        self._ent_default_tags.insert(0, settings.get("default_hashtags", ""))
        ttk.Label(post_f, text=_t("lbl_default_hashtag_hint"), foreground="gray", font=("", 7)).pack(anchor="w")

        # --- 閉じるボタン ---
        tk.Button(
            main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
            font=("", 10, "bold"), command=self._save_and_close,
        ).pack(fill=tk.X, pady=(8, 0))
        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

    def _on_test_auth(self):
        """接続テスト"""
        self._save_keys()
        self._btn_test.config(state="disabled", text=_t("btn_testing"))
        self._lbl_auth_status.config(text=_t("btn_testing"), foreground="orange")

        def _do():
            ok = self._build_client()
            if self._panel and self._panel.winfo_exists():
                if ok:
                    self._panel.after(0, lambda: self._lbl_auth_status.config(
                        text=_t("auth_ok", screen_name=self._auth_user), foreground="green"
                    ))
                else:
                    self._panel.after(0, lambda: self._lbl_auth_status.config(
                        text=_t("auth_fail", err="Invalid credentials"), foreground="red"
                    ))
                self._panel.after(0, lambda: self._btn_test.config(
                    state="normal", text=_t("btn_test_auth")
                ))

        threading.Thread(target=_do, daemon=True).start()

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
        self.save_settings(settings)
        self._panel.destroy()

"""
NiconicoLivePlugin.py - ニコニコ生放送連携プラグイン for TeloPon
================================================================
NDGR メッセージサーバー経由でリアルタイムにコメント・ギフト・ニコニ広告・
アンケート・統計情報を取得し、AIに注入する。

基本機能（ログイン不要）:
  - コメント読み取り
  - ギフト検知
  - ニコニ広告検知
  - エモーション検知
  - リアルタイム統計（視聴者数・コメント数）
  - アンケート結果取得

拡張機能（ログイン時 — [CMD]NC:xxx）:
  - アンケート作成/結果表示/終了
  - 運営コメント投稿/削除
  - コメント投稿
  - 視聴者数取得

ref: NDGRClient (MIT License) https://github.com/tsukumijima/NDGRClient
"""

import asyncio
import os
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# _niconico パッケージを確実にインポートできるようにする
# (plugin_manager がロード後に sys.path を pop するため)
_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)

import logger

# ==========================================
# 多言語対応
# ==========================================
_L = {
    "ja": {
        "import_error_title": "ライブラリ不足",
        "import_error_msg": (
            "必要なライブラリがインストールされていません。\n"
            "コマンドプロンプトで以下を実行してください。\n\n"
            "pip install aiohttp websockets protobuf"
        ),
        "plugin_name": "ニコニコ生放送連携",
        "window_title": "⚙️ ニコニコ生放送 設定",
        "label_url": "🔗 ニコニコ生放送 URL:",
        "label_url_hint": "例: https://live.nicovideo.jp/watch/lv...",
        "btn_connect": "接続",
        "btn_disconnect": "切断",
        "btn_fetching": "取得中...",
        "btn_close": "閉じる",
        "status_prompt": "URLを入力して「接続」を押してください",
        "status_fetching": "配信情報を取得しています...",
        "status_connected": "✅ 接続成功 ({program_id})",
        "status_waiting": "⏳ 配信開始待機中... ({program_id})",
        "status_error": "❌ 取得エラー: {err_msg}",
        "status_disconnected": "切断されました",
        "section_info": " 📺 配信情報 ",
        "lbl_title_empty": "タイトル: 未取得",
        "lbl_title": "タイトル: {title}",
        "lbl_desc_empty": "説明文: 未取得",
        "lbl_desc": "説明文: {desc}",
        # --- 認証 ---
        "lf_auth": " 🔑 ニコニコ ログイン（任意）",
        "label_auth_hint": "※ ログインするとアンケート作成・運営コメント等が使えます",
        "label_mail": "メールアドレス:",
        "label_password": "パスワード:",
        "btn_login": "ログイン",
        "btn_logout": "ログアウト",
        "btn_logging_in": "認証中...",
        "btn_cancel": "キャンセル",
        "auth_status_none": "未認証（読み取り専用）",
        "auth_status_ok": "✅ 認証済み",
        "auth_status_fail": "❌ ログイン失敗",
        "auth_status_mfa": "🔐 確認コードを入力してください",
        "label_mfa_code": "確認コード（6桁）:",
        "btn_mfa_submit": "送信",
        "auth_or_cookie": "",  # unused
        # --- 機能設定 ---
        "lf_features": " 📋 機能設定 ",
        "lf_features_readonly": " 📖 読み取り機能（ログイン不要）",
        "lf_features_auth": " ✏️ 操作機能（要ログイン）",
        "chk_comments": "コメント読み取り",
        "chk_gifts": "ギフト通知",
        "chk_ads": "ニコニ広告通知",
        "chk_emotions": "エモーション通知",
        "chk_statistics": "統計情報更新",
        "chk_enquete": "アンケート結果通知",
        "chk_viewers_cmd": "視聴者数取得",
        "chk_poll": "アンケート作成/終了",
        "chk_opcomment": "運営コメント投稿",
        "chk_viewer_ok": "視聴者可",
        "label_anon_name": "匿名ユーザーの表示名:",
        # --- プロンプト ---
        "prompt_addon": (
            "# 【配信の事前情報】\n"
            "あなたは今、以下のニコニコ生放送に参加しています。この情報を踏まえて番組を進行してください。\n"
            "* 配信タイトル: {title}\n"
            "* 配信の説明文: {desc}\n"
        ),
        "prompt_cmd_viewers": (
            "\n# 【ニコニコ生放送 情報コマンド】\n"
            "* 視聴者数取得: [CMD]NC:viewers\n"
            "* 「今何人？」「視聴者数は？」→ [CMD]NC:viewers\n"
        ),
        "prompt_cmd_auth": (
            "\n# 【ニコニコ生放送 操作コマンド】\n"
            "以下のコマンドが使えます。テロップテキストの末尾（[MEMO]の直前）に記述してください。\n"
            "配信者の指示に応じて適切なコマンドを使ってください。\n"
            "\n"
            "## コマンド一覧\n"
            "* アンケート作成: [CMD]NC:poll create 質問文|選択肢1|選択肢2|...(2～9個)\n"
            "* アンケート結果表示: [CMD]NC:poll result\n"
            "* アンケート終了: [CMD]NC:poll close\n"
            "* 運営コメント投稿: [CMD]NC:opcomment テキスト\n"
            "* 色付き運営コメント: [CMD]NC:opcomment /色名 テキスト\n"
            "  (色名: white,red,pink,orange,yellow,green,cyan,blue,purple,black)\n"
            "* 固定運営コメント: [CMD]NC:opcomment /perm テキスト\n"
            "* 色+固定: [CMD]NC:opcomment /yellow /perm テキスト\n"
            "* 運営コメント削除: [CMD]NC:opcomment delete\n"
            "\n"
            "## 配信者の発言に対する反応ルール\n"
            "* 「アンケートして」「投票して」→ 設問と選択肢を考えて [CMD]NC:poll create 質問|A|B|C\n"
            "* 「集計して」「結果教えて」→ [CMD]NC:poll result\n"
            "* 「アンケート締め切って」「終了して」→ [CMD]NC:poll close\n"
            "* 「運営コメントで○○って出して」→ [CMD]NC:opcomment ○○\n"
            "* 「赤で○○って出して」「黄色で」→ [CMD]NC:opcomment /red ○○  (/yellow 等)\n"
            "* 「固定で○○って出して」→ [CMD]NC:opcomment /perm ○○\n"
            "* 「運営コメント消して」→ [CMD]NC:opcomment delete\n"
            "\n"
            "## 例\n"
            "配信者「好きな色をアンケートして」→\n"
            "[TOPIC]アンケート [MAIN]好きな色は？投票してね！ [CMD]NC:poll create 好きな色は？|赤|青|緑|黄色\n"
        ),
        # --- AI注入テキスト ---
        "gift_cue": (
            "【番組ディレクターからのカンペ】\n"
            "{name}さんからギフト「{item}」({point}pt)が届きました！感謝の言葉を述べてください。"
        ),
        "ad_cue": (
            "【番組ディレクターからのカンペ】\n"
            "ニコニ広告されました！({point}pt) {message} 感謝しましょう。"
        ),
        "emotion_cue": (
            "【番組ディレクターからのカンペ】\n"
            "エモーションが大量に送られています！盛り上がりに反応してください。"
        ),
        "enquete_result_cue": (
            "【番組ディレクターからのカンペ】\n"
            "アンケート結果が出ました。質問:「{question}」\n{results}\n"
            "この結果について感想やコメントを述べてください。"
        ),
        "statistics_milestone_cue": (
            "【番組ディレクターからのカンペ】\n"
            "来場者数が{viewers}人を突破しました！みんなに感謝しましょう。"
        ),
        "viewers_cue": (
            "【番組ディレクターからのカンペ】\n"
            "現在の同時視聴者数は{viewers}人、コメント数は{comments}件です。配信者に伝えてください。"
        ),
        "viewers_unavailable": (
            "【番組ディレクターからのカンペ】\n"
            "視聴者数の取得に失敗しました。"
        ),
        "poll_created_cue": (
            "【番組ディレクターからのカンペ】\n"
            "アンケート「{question}」を作成しました。みんなに投票を呼びかけてください。"
        ),
        "poll_closed_cue": (
            "【番組ディレクターからのカンペ】\n"
            "アンケートを終了しました。"
        ),
        "opcomment_sent_cue": (
            "【番組ディレクターからのカンペ】\n"
            "運営コメント「{text}」を表示しました。"
        ),
    },
    "en": {
        "import_error_title": "Missing Libraries",
        "import_error_msg": (
            "Required libraries are not installed.\n"
            "Please run:\n\n"
            "pip install aiohttp websockets protobuf"
        ),
        "plugin_name": "Niconico Live Plugin",
        "window_title": "⚙️ Niconico Live Settings",
        "label_url": "🔗 Niconico Live URL:",
        "label_url_hint": "e.g. https://live.nicovideo.jp/watch/lv...",
        "btn_connect": "Connect",
        "btn_disconnect": "Disconnect",
        "btn_fetching": "Fetching...",
        "btn_close": "Close",
        "status_prompt": "Enter a URL and press Connect",
        "status_fetching": "Fetching broadcast info...",
        "status_connected": "✅ Connected ({program_id})",
        "status_waiting": "⏳ Waiting for broadcast... ({program_id})",
        "status_error": "❌ Fetch error: {err_msg}",
        "status_disconnected": "Disconnected",
        "section_info": " 📺 Broadcast Info ",
        "lbl_title_empty": "Title: N/A",
        "lbl_title": "Title: {title}",
        "lbl_desc_empty": "Description: N/A",
        "lbl_desc": "Description: {desc}",
        "lf_auth": " 🔑 Niconico Login (optional)",
        "label_auth_hint": "※ Login to enable poll creation, operator comments, etc.",
        "label_mail": "Email:",
        "label_password": "Password:",
        "btn_login": "Login",
        "btn_logout": "Logout",
        "btn_logging_in": "Logging in...",
        "btn_cancel": "Cancel",
        "auth_status_none": "Not authenticated (read-only)",
        "auth_status_ok": "✅ Authenticated",
        "auth_status_fail": "❌ Login failed",
        "auth_status_mfa": "🔐 Enter verification code",
        "label_mfa_code": "Verification code (6 digits):",
        "btn_mfa_submit": "Submit",
        "auth_or_cookie": "Or enter user_session cookie directly:",
        "lf_features": " 📋 Feature Settings ",
        "lf_features_readonly": " 📖 Read-only (no login required)",
        "lf_features_auth": " ✏️ Control features (login required)",
        "chk_comments": "Read comments",
        "chk_gifts": "Gift notifications",
        "chk_ads": "Niconi-ad notifications",
        "chk_emotions": "Emotion notifications",
        "chk_statistics": "Statistics updates",
        "chk_enquete": "Enquete result notifications",
        "chk_viewers_cmd": "Get viewer count",
        "chk_poll": "Create/close polls",
        "chk_opcomment": "Operator comments",
        "chk_viewer_ok": "Viewer OK",
        "label_anon_name": "Anonymous user display name:",
        "prompt_addon": (
            "# [Broadcast Info]\n"
            "You are currently participating in the following Niconico live stream. "
            "Please host the show based on this information.\n"
            "* Stream title: {title}\n"
            "* Description: {desc}\n"
        ),
        "prompt_cmd_viewers": (
            "\n# [Niconico Live Info Commands]\n"
            "* Get viewer count: [CMD]NC:viewers\n"
        ),
        "prompt_cmd_auth": (
            "\n# [Niconico Live Control Commands]\n"
            "You can use these commands. Append them at the end of telop text (before [MEMO]).\n"
            "\n"
            "## Commands\n"
            "* Create poll: [CMD]NC:poll create Question|Choice1|Choice2|...(2-9)\n"
            "* Show poll result: [CMD]NC:poll result\n"
            "* Close poll: [CMD]NC:poll close\n"
            "* Send operator comment: [CMD]NC:opcomment text\n"
            "* Colored: [CMD]NC:opcomment /color text (white,red,pink,orange,yellow,green,cyan,blue,purple,black)\n"
            "* Fixed/pinned: [CMD]NC:opcomment /perm text\n"
            "* Delete operator comment: [CMD]NC:opcomment delete\n"
        ),
        "gift_cue": (
            "[Cue from Director]\n"
            "{name} sent a gift \"{item}\" ({point}pt)! Please express your gratitude."
        ),
        "ad_cue": (
            "[Cue from Director]\n"
            "Someone placed a Niconi-ad! ({point}pt) {message} Express your thanks."
        ),
        "emotion_cue": (
            "[Cue from Director]\n"
            "Lots of emotions are being sent! React to the excitement."
        ),
        "enquete_result_cue": (
            "[Cue from Director]\n"
            "Poll results are in. Question: \"{question}\"\n{results}\n"
            "Comment on these results."
        ),
        "statistics_milestone_cue": (
            "[Cue from Director]\n"
            "Viewer count surpassed {viewers}! Thank everyone."
        ),
        "viewers_cue": (
            "[Cue from Director]\n"
            "Current concurrent viewers: {viewers}, comments: {comments}. Tell the streamer."
        ),
        "viewers_unavailable": (
            "[Cue from Director]\n"
            "Failed to get viewer count."
        ),
        "poll_created_cue": (
            "[Cue from Director]\n"
            "Poll \"{question}\" has been created. Encourage everyone to vote."
        ),
        "poll_closed_cue": (
            "[Cue from Director]\n"
            "Poll has been closed."
        ),
        "opcomment_sent_cue": (
            "[Cue from Director]\n"
            "Operator comment \"{text}\" is now displayed."
        ),
    },
}


def _t(key: str, **kwargs) -> str:
    """プラグイン内翻訳関数。i18n未導入環境でも動作する。"""
    try:
        import i18n
        lang = i18n.get_lang()
    except Exception:
        lang = "en"
    text = _L.get(lang, _L["en"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


# ==========================================
# 依存ライブラリ確認
# ==========================================
try:
    import aiohttp
    import websockets
    from google.protobuf import descriptor as _pb_descriptor  # noqa: F401
except ImportError:
    messagebox.showerror(_t("import_error_title"), _t("import_error_msg"))

from plugin_manager import BasePlugin

# ==========================================
# プラグイン本体
# ==========================================

_TAG = "[NiconicoLive]"

# 視聴者数マイルストーン通知の閾値
_VIEWER_MILESTONES = [100, 500, 1000, 2000, 3000, 5000, 10000, 20000, 50000, 100000]


class NiconicoLivePlugin(BasePlugin):
    PLUGIN_ID = "niconico_live"
    PLUGIN_NAME = "Niconico Live Plugin"
    PLUGIN_TYPE = "TOOL"
    IDENTIFIER = "NC"  # [CMD]NC:xxx

    def __init__(self):
        super().__init__()
        self.plugin_queue = None
        self.is_running = False
        self._live_queue = None
        self._live_prompt_config = None

        # 配信情報
        self._program_id: str | None = None
        self._nicolive_id: str = ""  # URL から抽出した lv...
        self._title: str = ""
        self._description: str = ""
        self._supplier_id: str = ""  # 配信者ユーザーID
        self._is_own_broadcast: bool = False  # 自分の配信かどうか
        self.is_connected = False

        # 内部クライアント
        self._client = None
        self._stream_thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

        # 統計キャッシュ
        self._last_stats = None
        self._notified_milestones: set[int] = set()

        # エモーション集計
        self._emotion_count = 0
        self._emotion_last_notify = 0.0

        # コメントバッチ
        self._comment_batch: list[tuple[str, str]] = []  # (user, text)
        self._comment_lock = threading.Lock()
        self._batch_timer: threading.Timer | None = None

    # ==========================================
    # 表示名
    # ==========================================
    def get_display_name(self) -> str:
        return _t("plugin_name")

    # ==========================================
    # 設定
    # ==========================================
    def get_default_settings(self):
        return {
            "enabled": False,
            "saved_url": "",
            "user_session": "",
            "anonymous_name": "匿名",
            # 機能トグル
            "fetch_comments": True,
            "notify_gifts": True,
            "notify_ads": True,
            "notify_emotions": True,
            "update_statistics": True,
            "notify_enquete": True,
            # CMD — AI 使用許可
            "ai_poll": True,
            "ai_opcomment": True,
            "ai_viewers": True,
            # CMD — 視聴者可
            "viewer_poll": False,
            "viewer_opcomment": False,
            "viewer_viewers": True,
        }

    def _update_enabled_state(self, is_enabled: bool):
        settings = self.get_settings()
        settings["enabled"] = is_enabled
        self.save_settings(settings)

    # ==========================================
    # 設定 UI
    # ==========================================
    def open_settings_ui(self, parent_window):
        self.panel = tk.Toplevel(parent_window)
        self.panel.title(_t("window_title"))
        self.panel.geometry("700x560")
        self.panel.attributes("-topmost", True)

        main_f = ttk.Frame(self.panel, padding=10)
        main_f.pack(fill=tk.BOTH, expand=True)

        settings = self.get_settings()

        # ============================================================
        # 上段: 認証
        # ============================================================
        self._auth_f = ttk.LabelFrame(main_f, text=_t("lf_auth"), padding=8)
        self._auth_f.pack(fill=tk.X, pady=(0, 6))

        # --- 未認証時: ログインフォーム ---
        self._login_frame = ttk.Frame(self._auth_f)
        ttk.Label(self._login_frame, text=_t("label_auth_hint"), foreground="gray", font=("", 8)).pack(anchor="w")
        cred_f = ttk.Frame(self._login_frame)
        cred_f.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(cred_f, text=_t("label_mail"), width=14, anchor="e").grid(row=0, column=0, sticky="e", padx=(0, 4))
        self._ent_mail = ttk.Entry(cred_f, font=("", 9))
        self._ent_mail.grid(row=0, column=1, sticky="ew", pady=1)
        ttk.Label(cred_f, text=_t("label_password"), width=14, anchor="e").grid(row=1, column=0, sticky="e", padx=(0, 4))
        self._ent_password = ttk.Entry(cred_f, font=("", 9), show="*")
        self._ent_password.grid(row=1, column=1, sticky="ew", pady=1)
        cred_f.columnconfigure(1, weight=1)
        self._btn_login = tk.Button(
            self._login_frame, text=_t("btn_login"), bg="#28a745", fg="white",
            font=("", 9, "bold"), width=12, command=self._do_login,
        )
        self._btn_login.pack(anchor="w", pady=(4, 0))
        self._lbl_auth = ttk.Label(self._login_frame, text="", foreground="gray")
        self._lbl_auth.pack(anchor="w", pady=(2, 0))

        # --- 認証済み時: プロフィール + ログアウト ---
        self._profile_frame = ttk.Frame(self._auth_f)
        self._profile_icon_label = ttk.Label(self._profile_frame)
        self._profile_icon_label.pack(side="left", padx=(0, 8))
        self._profile_name_label = ttk.Label(self._profile_frame, text="", font=("", 10, "bold"))
        self._profile_name_label.pack(side="left")
        self._btn_logout = tk.Button(
            self._profile_frame, text=_t("btn_logout"), width=10, command=self._do_logout,
        )
        self._btn_logout.pack(side="right")
        self._profile_photo = None
        self._is_logged_in = bool(settings.get("user_session"))

        # ============================================================
        # 中段: URL + 配信情報
        # ============================================================
        url_f = ttk.Frame(main_f)
        url_f.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(url_f, text=_t("label_url"), font=("", 10, "bold")).pack(side="left", padx=(0, 5))
        self._ent_url = ttk.Entry(url_f, font=("", 10))
        self._ent_url.pack(side="left", fill=tk.X, expand=True, padx=(0, 5))
        self._ent_url.insert(0, settings.get("saved_url", ""))
        self._btn_connect = tk.Button(
            url_f, text=_t("btn_connect"), bg="#007bff", fg="white",
            font=("", 9, "bold"), width=8, command=self._toggle_connection,
        )
        self._btn_connect.pack(side="right")

        self._lbl_status = ttk.Label(main_f, text=_t("status_prompt"), foreground="gray")
        self._lbl_status.pack(anchor="w", pady=(0, 4))

        # ============================================================
        # 下段: 2カラム（左=配信情報、右=機能設定）
        # ============================================================
        columns_f = ttk.Frame(main_f)
        columns_f.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # ---- 左カラム: 配信情報 ----
        left_f = ttk.LabelFrame(columns_f, text=_t("section_info"), padding=8)
        left_f.pack(side="left", fill=tk.BOTH, expand=True, padx=(0, 4))

        self._lbl_thumb = ttk.Label(left_f, text="", background="#ddd", anchor="center")
        self._lbl_thumb.pack(fill=tk.X, pady=(0, 6))
        self._thumb_photo = None

        self._lbl_title = ttk.Label(left_f, text=_t("lbl_title_empty"), font=("", 9, "bold"), wraplength=300)
        self._lbl_title.pack(anchor="w", pady=(0, 2))

        self._lbl_supplier = ttk.Label(left_f, text="", foreground="#666", font=("", 8))
        self._lbl_supplier.pack(anchor="w", pady=(0, 4))

        self._lbl_desc = tk.Label(
            left_f, text=_t("lbl_desc_empty"), justify="left",
            anchor="nw", fg="#555", wraplength=300, height=4,
        )
        self._lbl_desc.pack(fill=tk.BOTH, expand=True)

        # ---- 右カラム: 機能設定 ----
        right_f = ttk.Frame(columns_f)
        right_f.pack(side="right", fill=tk.Y, padx=(4, 0))

        # 読み取り機能
        ro_f = ttk.LabelFrame(right_f, text=_t("lf_features_readonly"), padding=6)
        ro_f.pack(fill=tk.X, pady=(0, 4))

        self._feature_vars = {}
        for key, label_key in [
            ("fetch_comments", "chk_comments"),
            ("notify_gifts", "chk_gifts"),
            ("notify_ads", "chk_ads"),
            ("notify_emotions", "chk_emotions"),
            ("update_statistics", "chk_statistics"),
            ("notify_enquete", "chk_enquete"),
        ]:
            var = tk.BooleanVar(value=settings.get(key, True))
            self._feature_vars[key] = var
            ttk.Checkbutton(ro_f, text=_t(label_key), variable=var).pack(anchor="w")

        anon_f = ttk.Frame(ro_f)
        anon_f.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(anon_f, text=_t("label_anon_name"), font=("", 8)).pack(side="left")
        self._ent_anon_name = ttk.Entry(anon_f, font=("", 8), width=10)
        self._ent_anon_name.pack(side="left", padx=(4, 0))
        self._ent_anon_name.insert(0, settings.get("anonymous_name", "匿名"))

        # 操作機能（要ログイン）
        auth_f2 = ttk.LabelFrame(right_f, text=_t("lf_features_auth"), padding=6)
        auth_f2.pack(fill=tk.X, pady=(0, 4))

        hdr_f = ttk.Frame(auth_f2)
        hdr_f.pack(fill=tk.X)
        ttk.Label(hdr_f, text="", width=18).pack(side="left")
        ttk.Label(hdr_f, text=_t("chk_viewer_ok"), font=("", 7), foreground="gray").pack(side="left", padx=(4, 0))

        self._auth_feature_checks = []
        self._viewer_vars = {}
        for ai_key, label_key, viewer_key in [
            ("ai_viewers", "chk_viewers_cmd", "viewer_viewers"),
            ("ai_poll", "chk_poll", "viewer_poll"),
            ("ai_opcomment", "chk_opcomment", "viewer_opcomment"),
        ]:
            row_f = ttk.Frame(auth_f2)
            row_f.pack(fill=tk.X)
            ai_var = tk.BooleanVar(value=settings.get(ai_key, True))
            self._feature_vars[ai_key] = ai_var
            chk = ttk.Checkbutton(row_f, text=_t(label_key), variable=ai_var, width=18)
            chk.pack(side="left")
            self._auth_feature_checks.append(chk)
            v_var = tk.BooleanVar(value=settings.get(viewer_key, False))
            self._viewer_vars[viewer_key] = v_var
            v_chk = ttk.Checkbutton(row_f, variable=v_var)
            v_chk.pack(side="left", padx=(4, 0))
            self._auth_feature_checks.append(v_chk)

        # ============================================================
        # 全構築完了 — 状態適用
        # ============================================================
        self._switch_auth_view()
        if self._is_logged_in:
            threading.Thread(target=self._fetch_profile_thread, daemon=True).start()

        ttk.Button(main_f, text=_t("btn_close"), command=self._close_panel).pack(pady=(4, 0))

        if self.is_connected and self._program_id:
            self._update_ui_connected()

    def _close_panel(self):
        """パネルを閉じるとき、全設定を保存"""
        settings = self.get_settings()
        for key, var in self._feature_vars.items():
            settings[key] = var.get()
        for key, var in self._viewer_vars.items():
            settings[key] = var.get()
        settings["anonymous_name"] = self._ent_anon_name.get().strip() or "匿名"
        self.save_settings(settings)
        self.panel.destroy()

    def _fetch_profile_thread(self):
        """認証済みユーザーのプロフィールを取得してUIに表示する"""
        loop = asyncio.new_event_loop()
        try:
            from _niconico.client import NicoLiveClient
            client = NicoLiveClient()
            settings = self.get_settings()
            loop.run_until_complete(client.login(user_session=settings.get("user_session", "")))
            profile = loop.run_until_complete(client.fetch_my_profile())
            loop.run_until_complete(client.close())
            logger.debug(f"{_TAG} プロフィール結果: {profile}")
            if profile and hasattr(self, "panel") and self.panel.winfo_exists():
                # アイコン画像を取得
                icon_bytes = None
                icon_url = profile.get("icon_url", "")
                logger.debug(f"{_TAG} アイコンURL: {icon_url}")
                if icon_url:
                    import io
                    import urllib.request
                    try:
                        req = urllib.request.Request(icon_url, headers={"User-Agent": "TeloPon"})
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            icon_bytes = resp.read()
                        logger.debug(f"{_TAG} アイコン取得成功: {len(icon_bytes)} bytes")
                    except Exception as e:
                        logger.debug(f"{_TAG} アイコン取得失敗: {e}")
                self.panel.after(0, self._show_profile, profile.get("nickname", ""), icon_bytes)
            elif not profile:
                logger.warning(f"{_TAG} プロフィール取得失敗（None）")
        except Exception as e:
            logger.warning(f"{_TAG} プロフィール取得エラー: {e}")
        finally:
            loop.close()

    def _show_profile(self, nickname: str, icon_bytes: bytes | None):
        """認証済みプロフィールをUIに表示"""
        if not hasattr(self, "_profile_frame") or not hasattr(self, "panel"):
            return
        if not self.panel.winfo_exists():
            return
        logger.debug(f"{_TAG} _show_profile: nickname={nickname}, icon={len(icon_bytes) if icon_bytes else 0} bytes")
        if icon_bytes:
            try:
                import io
                from PIL import Image, ImageTk
                img = Image.open(io.BytesIO(icon_bytes))
                img.thumbnail((36, 36))
                self._profile_photo = ImageTk.PhotoImage(img)
                self._profile_icon_label.config(image=self._profile_photo)
            except Exception as e:
                logger.debug(f"{_TAG} アイコン描画エラー: {e}")
                self._profile_icon_label.config(text="👤")
        else:
            self._profile_icon_label.config(text="👤")
        self._profile_name_label.config(text=nickname)

    def _do_login(self):
        """メール/パスワードでニコニコにログイン（2FA対応）"""
        mail = self._ent_mail.get().strip()
        password = self._ent_password.get().strip()
        if not mail or not password:
            return

        self._btn_login.config(state="disabled", text=_t("btn_logging_in"))
        self._lbl_auth.config(text=_t("btn_logging_in"), foreground="orange")

        # ログイン用の loop + client をスレッドで保持（MFA でも同じ loop を使う）
        self._login_loop = asyncio.new_event_loop()
        self._login_client = None

        def _run():
            asyncio.set_event_loop(self._login_loop)
            needs_mfa = False
            try:
                from _niconico.client import NicoLiveClient
                self._login_client = NicoLiveClient()
                result = self._login_loop.run_until_complete(
                    self._login_client.login(mail=mail, password=password)
                )
                if result is True:
                    self._finish_login()
                elif isinstance(result, str):
                    logger.info(f"{_TAG} 🔐 2FA が必要です")
                    needs_mfa = True
                    if hasattr(self, "panel") and self.panel.winfo_exists():
                        self.panel.after(0, self._show_mfa_ui)
                else:
                    self._login_loop.run_until_complete(self._login_client.close())
                    self._login_client = None
                    if hasattr(self, "panel") and self.panel.winfo_exists():
                        self.panel.after(0, self._on_login_fail)
                    logger.warning(f"{_TAG} ❌ ログイン失敗")
            except Exception as e:
                if hasattr(self, "panel") and self.panel.winfo_exists():
                    self.panel.after(0, self._on_login_fail)
                logger.warning(f"{_TAG} ❌ ログインエラー: {e}")
            finally:
                # MFA 待ちの場合は loop を閉じない（_submit_mfa で再利用）
                if not needs_mfa:
                    if self._login_loop and not self._login_loop.is_closed():
                        self._login_loop.close()

        threading.Thread(target=_run, daemon=True).start()

    def _show_mfa_ui(self):
        """2FA コード入力UIを表示する"""
        self._lbl_auth.config(text=_t("auth_status_mfa"), foreground="orange")
        # ログインボタンをキャンセルボタンに変更
        self._btn_login.config(
            state="normal", text=_t("btn_cancel"), bg="#dc3545",
            command=self._cancel_mfa,
        )

        if hasattr(self, "_mfa_frame"):
            self._mfa_frame.destroy()
        self._mfa_frame = ttk.Frame(self._login_frame)
        self._mfa_frame.pack(fill=tk.X, pady=(6, 0))

        ttk.Label(self._mfa_frame, text=_t("label_mfa_code"), font=("", 9)).pack(side="left")
        self._ent_mfa = ttk.Entry(self._mfa_frame, font=("", 11), width=10)
        self._ent_mfa.pack(side="left", padx=(5, 5))
        self._ent_mfa.focus_set()

        self._btn_mfa = tk.Button(
            self._mfa_frame, text=_t("btn_mfa_submit"), bg="#28a745", fg="white",
            font=("", 9, "bold"), width=8, command=self._submit_mfa,
        )
        self._btn_mfa.pack(side="left")
        self._ent_mfa.bind("<Return>", lambda e: self._submit_mfa())

    def _cancel_mfa(self):
        """2FA をキャンセルしてログインフォームに戻る"""
        # MFA フレームを消す
        if hasattr(self, "_mfa_frame"):
            self._mfa_frame.destroy()
        # ログインクライアントを閉じる
        if hasattr(self, "_login_client") and self._login_client:
            try:
                if hasattr(self, "_login_loop") and self._login_loop and not self._login_loop.is_closed():
                    self._login_loop.run_until_complete(self._login_client.close())
                    self._login_loop.close()
            except Exception:
                pass
            self._login_client = None
            self._login_loop = None
        # ボタンをログインに戻す
        self._btn_login.config(
            state="normal", text=_t("btn_login"), bg="#28a745",
            command=self._do_login,
        )
        self._lbl_auth.config(text="", foreground="gray")
        logger.info(f"{_TAG} 2FA キャンセル")

    def _submit_mfa(self):
        """2FA コードを送信する（ログイン時の loop を再利用）"""
        otp = self._ent_mfa.get().strip()
        if not otp or len(otp) != 6:
            return

        self._btn_mfa.config(state="disabled")
        self._lbl_auth.config(text=_t("btn_logging_in"), foreground="orange")

        def _run():
            try:
                # ログイン時と同じ loop + client を使う
                ok = self._login_loop.run_until_complete(
                    self._login_client.submit_mfa(otp)
                )
                if ok:
                    self._finish_login()
                else:
                    if hasattr(self, "panel") and self.panel.winfo_exists():
                        self.panel.after(0, self._on_mfa_fail)
                    logger.warning(f"{_TAG} ❌ 2FA コードが正しくありません")
            except Exception as e:
                if hasattr(self, "panel") and self.panel.winfo_exists():
                    self.panel.after(0, self._on_mfa_fail)
                logger.warning(f"{_TAG} ❌ 2FA エラー: {e}")

        threading.Thread(target=_run, daemon=True).start()

    def _finish_login(self):
        """ログイン成功後の共通処理"""
        user_session = self._login_client._cookies.get("user_session", "")

        # プロフィールからユーザーIDを取得して保存
        my_user_id = ""
        try:
            profile = self._login_loop.run_until_complete(
                self._login_client.fetch_my_profile()
            )
            if profile:
                my_user_id = str(profile.get("user_id", ""))
        except Exception:
            pass

        settings = self.get_settings()
        settings["user_session"] = user_session
        if my_user_id:
            settings["my_user_id"] = my_user_id
        self.save_settings(settings)
        self._is_logged_in = True
        logger.info(f"{_TAG} ✅ ログイン成功 (user_id: {my_user_id})")

        # クリーンアップ
        try:
            self._login_loop.run_until_complete(self._login_client.close())
        except Exception:
            pass
        self._login_client = None
        if self._login_loop and not self._login_loop.is_closed():
            self._login_loop.close()
        self._login_loop = None

        if hasattr(self, "panel") and self.panel.winfo_exists():
            self.panel.after(0, self._on_login_success, user_session)

    def _on_login_success(self, user_session: str):
        self._ent_password.delete(0, tk.END)
        if hasattr(self, "_mfa_frame"):
            self._mfa_frame.destroy()
        self._switch_auth_view()
        # プロフィール取得して表示
        threading.Thread(target=self._fetch_profile_thread, daemon=True).start()

    def _on_login_fail(self):
        self._lbl_auth.config(text=_t("auth_status_fail"), foreground="red")
        self._btn_login.config(state="normal", text=_t("btn_login"))

    def _on_mfa_fail(self):
        """MFA コードが間違っていた場合 — 再入力可能にする"""
        self._lbl_auth.config(text=_t("auth_status_fail"), foreground="red")
        self._btn_mfa.config(state="normal")
        self._ent_mfa.delete(0, tk.END)
        self._ent_mfa.focus_set()

    def _do_logout(self):
        """ログアウト"""
        settings = self.get_settings()
        settings["user_session"] = ""
        settings["my_user_id"] = ""
        self.save_settings(settings)
        self._is_logged_in = False
        self._is_own_broadcast = False
        self._switch_auth_view()
        logger.info(f"{_TAG} ログアウトしました")

    def _switch_auth_view(self):
        """認証状態に応じてログインフォーム / プロフィールを切り替え"""
        if self._is_logged_in:
            self._login_frame.pack_forget()
            self._profile_frame.pack(fill=tk.X, pady=(2, 0))
        else:
            self._profile_frame.pack_forget()
            self._profile_icon_label.config(image="", text="")
            self._profile_name_label.config(text="")
            self._profile_photo = None
            self._login_frame.pack(fill=tk.X)
            self._btn_login.config(state="normal", text=_t("btn_login"))
            self._lbl_auth.config(text="", foreground="gray")
        self._update_auth_feature_state()

    def _update_auth_feature_state(self):
        """ログイン状態 + 自分の配信かどうかで操作機能をグレーアウト"""
        can_control = self._is_logged_in and (self._is_own_broadcast or not self.is_connected)
        state = "!disabled" if can_control else "disabled"
        for chk in self._auth_feature_checks:
            try:
                chk.state([state])
            except Exception:
                pass

    # ==========================================
    # URL 接続 / 切断
    # ==========================================
    def _toggle_connection(self):
        if self.is_connected:
            self._disconnect()
        else:
            url = self._ent_url.get().strip()
            if not url:
                return

            # lv... を抽出
            m = re.search(r"(lv\d+)", url)
            if not m:
                messagebox.showerror("Error", "URLから番組ID (lv...) を抽出できません。")
                return

            self._nicolive_id = m.group(1)

            settings = self.get_settings()
            settings["saved_url"] = url
            settings["enabled"] = False
            self.save_settings(settings)

            self._btn_connect.config(state="disabled", text=_t("btn_fetching"))
            self._lbl_status.config(text=_t("status_fetching"), foreground="orange")

            threading.Thread(target=self._fetch_info_thread, daemon=True).start()

    def _fetch_info_thread(self):
        """別スレッドで配信情報を取得"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            info = None
            is_404 = False
            try:
                from _niconico.client import NicoLiveClient
                client = NicoLiveClient()
                # ログイン済みなら Cookie を設定（非公開配信でもアクセス可能にする）
                settings = self.get_settings()
                us = settings.get("user_session", "")
                if us:
                    loop.run_until_complete(client.login(user_session=us))
                try:
                    info = loop.run_until_complete(client.fetch_program_info(self._nicolive_id))
                except Exception as e:
                    if "404" in str(e):
                        is_404 = True
                    else:
                        raise
                loop.run_until_complete(client.close())
            finally:
                loop.close()

            if is_404:
                # 配信ページ未公開 — 番組IDだけで待機状態にする
                self._program_id = self._nicolive_id
                self._title = ""
                self._description = ""
                self._supplier_id = ""
                self._supplier_name = ""
                self._thumb_bytes = None
                self.is_connected = True
                self._update_enabled_state(True)

                if hasattr(self, "panel") and self.panel.winfo_exists():
                    self.panel.after(0, self._update_ui_waiting)
                logger.info(f"{_TAG} ⏳ 配信開始待機中: {self._nicolive_id}")
                return

            self._program_id = info.program_id
            self._title = info.title
            self._description = info.description[:200] + ("..." if len(info.description) > 200 else "")
            self._supplier_id = info.supplier_id
            self._supplier_name = info.supplier_name

            # サムネイル取得
            self._thumb_bytes = None
            if info.thumbnail_url:
                try:
                    import urllib.request
                    req = urllib.request.Request(info.thumbnail_url, headers={"User-Agent": "TeloPon"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        self._thumb_bytes = resp.read()
                except Exception:
                    pass

            # 自分の配信かどうか判定
            settings = self.get_settings()
            my_user_id = settings.get("my_user_id", "")
            self._is_own_broadcast = bool(
                my_user_id and self._supplier_id and my_user_id == self._supplier_id
            )
            if self._is_own_broadcast:
                logger.info(f"{_TAG} 自分の配信です（配信者操作が利用可能）")
            else:
                logger.info(f"{_TAG} 他人の配信です（読み取り専用）")

            self.is_connected = True
            self._update_enabled_state(True)

            if hasattr(self, "panel") and self.panel.winfo_exists():
                self.panel.after(0, self._update_ui_connected)

            # ライブ中に接続した場合は自動でstart
            if self._live_queue is not None and not self.is_running:
                self.start(self._live_prompt_config, self._live_queue)

            logger.info(f"{_TAG} ✅ 接続成功: {self._title} ({self._program_id})")

        except Exception as e:
            self._program_id = None
            self._update_enabled_state(False)
            if hasattr(self, "panel") and self.panel.winfo_exists():
                self.panel.after(0, lambda: self._update_ui_error(str(e)))
            logger.warning(f"{_TAG} ⚠️ 情報取得エラー: {e}")

    def _update_ui_connected(self):
        self._btn_connect.config(state="normal", text=_t("btn_disconnect"), bg="#dc3545")
        self._ent_url.config(state="readonly")
        self._lbl_status.config(
            text=_t("status_connected", program_id=self._program_id), foreground="green",
        )
        self._lbl_title.config(text=_t("lbl_title", title=self._title))
        self._lbl_desc.config(text=_t("lbl_desc", desc=self._description))

        # 配信者名
        if hasattr(self, "_lbl_supplier") and self._supplier_name:
            self._lbl_supplier.config(text=f"配信者: {self._supplier_name}")

        # サムネイル
        if hasattr(self, "_lbl_thumb") and getattr(self, "_thumb_bytes", None):
            try:
                import io
                from PIL import Image, ImageTk
                img = Image.open(io.BytesIO(self._thumb_bytes))
                img.thumbnail((320, 180))
                self._thumb_photo = ImageTk.PhotoImage(img)
                self._lbl_thumb.config(image=self._thumb_photo, text="")
            except Exception:
                self._lbl_thumb.config(text="[ サムネイル取得失敗 ]")
        elif hasattr(self, "_lbl_thumb"):
            self._lbl_thumb.config(text="")

        # 操作機能のグレーアウトを更新
        if hasattr(self, "_auth_feature_checks"):
            self._update_auth_feature_state()

    def _update_ui_waiting(self):
        """配信開始待機中のUI"""
        self._btn_connect.config(state="normal", text=_t("btn_disconnect"), bg="#dc3545")
        self._ent_url.config(state="readonly")
        self._lbl_status.config(
            text=_t("status_waiting", program_id=self._program_id), foreground="orange",
        )
        self._lbl_title.config(text=_t("lbl_title_empty"))
        if hasattr(self, "_lbl_supplier"):
            self._lbl_supplier.config(text="")
        if hasattr(self, "_auth_feature_checks"):
            self._update_auth_feature_state()

    def _update_ui_error(self, err_msg: str):
        self._btn_connect.config(state="normal", text=_t("btn_connect"), bg="#007bff")
        self._lbl_status.config(text=_t("status_error", err_msg=err_msg), foreground="red")

    def _disconnect(self):
        self.is_running = False
        self.is_connected = False
        self._program_id = None
        self._title = ""
        self._description = ""
        self._supplier_name = ""
        self._thumb_bytes = None
        self._stop_client()
        self._update_enabled_state(False)

        self._btn_connect.config(state="normal", text=_t("btn_connect"), bg="#007bff")
        self._ent_url.config(state="normal")
        self._lbl_status.config(text=_t("status_disconnected"), foreground="gray")
        self._lbl_title.config(text=_t("lbl_title_empty"))
        self._lbl_desc.config(text=_t("lbl_desc_empty"))
        if hasattr(self, "_lbl_supplier"):
            self._lbl_supplier.config(text="")
        if hasattr(self, "_lbl_thumb"):
            self._lbl_thumb.config(image="", text="")
            self._thumb_photo = None

        logger.info(f"{_TAG} ⏹️ 切断しました。")

    # ==========================================
    # AI連携: プロンプトアドオン
    # ==========================================
    def get_prompt_addon(self) -> str:
        if not self.is_connected or not self._program_id:
            return ""

        settings = self.get_settings()
        parts = [_t("prompt_addon", title=self._title, desc=self._description)]

        # viewers は常に利用可能（ログイン不要）
        if settings.get("ai_viewers", True):
            parts.append(_t("prompt_cmd_viewers"))

        # 操作系は認証済み + 自分の配信の場合のみ
        if settings.get("user_session") and self._is_own_broadcast:
            parts.append(_t("prompt_cmd_auth"))

        return "".join(parts)

    # ==========================================
    # ライフサイクル: start / stop
    # ==========================================
    def start(self, prompt_config, plugin_queue):
        self._live_queue = plugin_queue
        self._live_prompt_config = prompt_config

        if not self.is_connected or not self._nicolive_id:
            logger.debug(f"{_TAG} URLが接続されていないため待機します。")
            return

        self.cmt_msg = prompt_config.get("CMT_MSG", "※新着コメントです。これに反応してください。")
        self.plugin_queue = plugin_queue
        self.is_running = True

        # NDGR ストリーミングスレッドを開始
        self._stream_thread = threading.Thread(target=self._run_stream_loop, daemon=True)
        self._stream_thread.start()

        # コメントバッチタイマー開始
        self._start_batch_timer()

        logger.info(f"{_TAG} ▶️ ライブ連携を開始しました ({self._nicolive_id})")

    def stop(self):
        self.is_running = False
        self._live_queue = None
        self._live_prompt_config = None
        self._stop_client()
        if self._batch_timer:
            self._batch_timer.cancel()
            self._batch_timer = None
        # 残りコメントをフラッシュ
        self._flush_comments()
        logger.info(f"{_TAG} ⏹️ ライブ連携を停止しました。")

    def _stop_client(self):
        if self._client:
            self._client.stop()
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    # ==========================================
    # NDGR ストリーミング (daemon thread)
    # ==========================================
    def _run_stream_loop(self):
        """daemon thread のエントリポイント"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._async_stream())
        except Exception as e:
            if self.is_running:
                logger.warning(f"{_TAG} ストリームループ異常終了: {e}")
        finally:
            self._loop.close()
            self._loop = None

    async def _async_stream(self):
        """非同期ストリーミング本体"""
        from _niconico.client import NicoLiveClient, NicoCallbacks

        settings = self.get_settings()
        callbacks = NicoCallbacks(
            on_comment=self._on_comment if settings.get("fetch_comments", True) else None,
            on_gift=self._on_gift if settings.get("notify_gifts", True) else None,
            on_ad=self._on_ad if settings.get("notify_ads", True) else None,
            on_enquete=self._on_enquete if settings.get("notify_enquete", True) else None,
            on_statistics=self._on_statistics if settings.get("update_statistics", True) else None,
            on_notification=self._on_notification if settings.get("notify_emotions", True) else None,
        )

        self._client = NicoLiveClient(callbacks=callbacks)

        # 認証
        user_session = settings.get("user_session", "")
        if user_session:
            await self._client.login(user_session=user_session)

        await self._client.stream(self._nicolive_id)
        await self._client.close()

    # ==========================================
    # コールバック: コメント（バッチ処理）
    # ==========================================
    def _on_comment(self, comment):
        """コメント受信コールバック — バッチに蓄積"""
        text = comment.content
        if len(text) > 100:
            text = text[:100] + "…"
        # 表示名: コテハン > raw_user_id > 匿名名（設定値）
        if comment.name:
            display_name = comment.name
        elif comment.raw_user_id > 0:
            display_name = str(comment.raw_user_id)
        else:
            display_name = self.get_settings().get("anonymous_name", "匿名")

        with self._comment_lock:
            self._comment_batch.append((display_name, text, comment.avatar_url))

    def _start_batch_timer(self):
        """5秒ごとにコメントバッチをフラッシュ"""
        if not self.is_running:
            return
        self._flush_comments()
        self._batch_timer = threading.Timer(5.0, self._start_batch_timer)
        self._batch_timer.daemon = True
        self._batch_timer.start()

    def _flush_comments(self):
        """蓄積したコメントを一括でAIに注入"""
        with self._comment_lock:
            batch = self._comment_batch[:]
            self._comment_batch.clear()

        if not batch or not self.plugin_queue:
            return

        # アバターマップ送信 (avatar_urlがあるもののみ)
        avatar_map = {}
        for display_name, text, avatar_url in batch:
            if avatar_url:
                avatar_map[display_name] = avatar_url
        if avatar_map:
            self.send_avatar_map(self.plugin_queue, avatar_map)

        # コメント送信
        comments = [f"[COMMENT] {name}: {text}" for name, text, _ in batch]
        count_prefix = f"（{len(comments)}件）\n" if len(comments) > 1 else ""
        combined = "\n".join(comments)
        payload = f"{count_prefix}{combined}\n\n{self.cmt_msg}" if self.cmt_msg else f"{count_prefix}{combined}"
        self.send_text(self.plugin_queue, payload)
        logger.info(f"{_TAG} 💬 コメントを注入しました（{len(comments)}件）")

    # ==========================================
    # コールバック: ギフト
    # ==========================================
    def _on_gift(self, gift):
        if not self.plugin_queue:
            return
        cue = _t("gift_cue", name=gift.advertiser_name, item=gift.item_name, point=gift.point)
        self.send_text(self.plugin_queue, cue)
        logger.info(f"{_TAG} 🎁 ギフト: {gift.advertiser_name} - {gift.item_name} ({gift.point}pt)")

    # ==========================================
    # コールバック: ニコニ広告
    # ==========================================
    def _on_ad(self, ad):
        if not self.plugin_queue:
            return
        cue = _t("ad_cue", point=ad.point, message=ad.message)
        self.send_text(self.plugin_queue, cue)
        logger.info(f"{_TAG} 📢 ニコニ広告: {ad.point}pt {ad.message}")

    # ==========================================
    # コールバック: アンケート
    # ==========================================
    def _on_enquete(self, enquete):
        if not self.plugin_queue:
            return
        if enquete.status in ("Result", "Closed") and enquete.results_per_mille:
            # 結果をフォーマット
            lines = []
            for i, choice in enumerate(enquete.choices):
                pct = enquete.results_per_mille[i] / 10.0 if i < len(enquete.results_per_mille) else 0
                lines.append(f"  {choice}: {pct:.1f}%")
            results_text = "\n".join(lines)
            cue = _t("enquete_result_cue", question=enquete.question, results=results_text)
            self.send_text(self.plugin_queue, cue)
            logger.info(f"{_TAG} 📊 アンケート結果: {enquete.question}")

    # ==========================================
    # コールバック: 統計情報
    # ==========================================
    def _on_statistics(self, stats):
        self._last_stats = stats

        if not self.plugin_queue:
            return

        # マイルストーン通知
        for milestone in _VIEWER_MILESTONES:
            if stats.viewers >= milestone and milestone not in self._notified_milestones:
                self._notified_milestones.add(milestone)
                cue = _t("statistics_milestone_cue", viewers=milestone)
                self.send_text(self.plugin_queue, cue)
                logger.info(f"{_TAG} 🎉 来場者数マイルストーン: {milestone}人")
                break

    # ==========================================
    # コールバック: 通知 (エモーション等)
    # ==========================================
    def _on_notification(self, notification):
        if not self.plugin_queue:
            return

        if notification.type == "EMOTION":
            self._emotion_count += 1
            now = time.time()
            # 30秒以内に5件以上のエモーションで通知
            if self._emotion_count >= 5 and now - self._emotion_last_notify > 30:
                cue = _t("emotion_cue")
                self.send_text(self.plugin_queue, cue)
                self._emotion_count = 0
                self._emotion_last_notify = now
                logger.info(f"{_TAG} ✨ エモーション集中検知")

        elif notification.type in ("RANKING_IN", "RANKING_UPDATED"):
            if notification.message:
                self.send_text(self.plugin_queue, f"【ニコニコ】{notification.message}")

        elif notification.type == "VISITED":
            pass  # 来場通知は頻度が高すぎるのでスキップ

        elif notification.type == "USER_FOLLOW":
            if notification.message:
                self.send_text(self.plugin_queue, f"【ニコニコ】{notification.message}")

    # ==========================================
    # CMD ディスパッチ ([CMD]NC:xxx)
    # ==========================================
    @staticmethod
    def _clean_cmd_value(value: str) -> str:
        cleaned = re.sub(r'\[(?:WND|LAY|BDG|MEMO|TOPIC|MAIN)\].*$', '', value, flags=re.IGNORECASE)
        return cleaned.strip()

    def handle(self, value: str):
        """CMD ディスパッチャーから呼ばれる"""
        if not value:
            return
        value = self._clean_cmd_value(value)
        if not value:
            return

        v = value.strip()
        v_lower = v.lower()

        # 認証不要コマンド
        if v_lower.startswith("viewers"):
            self._cmd_viewers()
            return

        # 認証必要 + 自分の配信のみ
        settings = self.get_settings()
        if not settings.get("user_session"):
            logger.warning(f"{_TAG} 未認証のためCMDスキップ: {v}")
            return
        if not self._is_own_broadcast:
            logger.warning(f"{_TAG} 自分の配信ではないためCMDスキップ: {v}")
            return

        matched = False
        for cmd_name, handler in [
            ("poll", lambda a: self._cmd_poll(a)),
            ("opcomment", lambda a: self._cmd_opcomment(a)),
        ]:
            if v_lower.startswith(cmd_name):
                arg = v[len(cmd_name):].strip()
                handler(arg)
                matched = True
                break

        if not matched:
            logger.warning(f"{_TAG} 未知のサブコマンド: '{v}'")

    # --- viewers ---
    def _cmd_viewers(self):
        if self._last_stats:
            cue = _t("viewers_cue", viewers=self._last_stats.viewers, comments=self._last_stats.comments)
        else:
            cue = _t("viewers_unavailable")
        if self.plugin_queue:
            self.send_text(self.plugin_queue, cue)

    # --- poll ---
    def _cmd_poll(self, arg: str):
        parts = arg.strip().split(None, 1)
        action = parts[0].lower() if parts else ""
        param = parts[1] if len(parts) > 1 else ""

        if action == "create":
            self._poll_create(param)
        elif action == "result":
            self._poll_result()
        elif action == "close":
            self._poll_close()
        else:
            logger.warning(f"{_TAG} 未知のpollアクション: {action}")

    def _poll_create(self, param: str):
        segments = [s.strip() for s in param.split("|") if s.strip()]
        if len(segments) < 3:
            logger.warning(f"{_TAG} poll create: 質問+選択肢2個以上が必要")
            return
        question = segments[0]
        items = segments[1:10]  # 最大9個

        def _run():
            loop = asyncio.new_event_loop()
            try:
                from _niconico.broadcaster_api import BroadcasterAPI
                session = loop.run_until_complete(self._create_auth_session())
                api = BroadcasterAPI(session)
                ok = loop.run_until_complete(api.create_enquete(self._program_id, question, items))
                loop.run_until_complete(session.close())
                if ok and self.plugin_queue:
                    self.send_text(self.plugin_queue, _t("poll_created_cue", question=question))
            finally:
                loop.close()

        threading.Thread(target=_run, daemon=True).start()

    def _poll_result(self):
        def _run():
            loop = asyncio.new_event_loop()
            try:
                from _niconico.broadcaster_api import BroadcasterAPI
                session = loop.run_until_complete(self._create_auth_session())
                api = BroadcasterAPI(session)
                loop.run_until_complete(api.show_enquete_result(self._program_id))
                loop.run_until_complete(session.close())
            finally:
                loop.close()

        threading.Thread(target=_run, daemon=True).start()

    def _poll_close(self):
        def _run():
            loop = asyncio.new_event_loop()
            try:
                from _niconico.broadcaster_api import BroadcasterAPI
                session = loop.run_until_complete(self._create_auth_session())
                api = BroadcasterAPI(session)
                ok = loop.run_until_complete(api.close_enquete(self._program_id))
                loop.run_until_complete(session.close())
                if ok and self.plugin_queue:
                    self.send_text(self.plugin_queue, _t("poll_closed_cue"))
            finally:
                loop.close()

        threading.Thread(target=_run, daemon=True).start()

    # --- opcomment ---
    # 運営コメントで使える色名
    _OPCOMMENT_COLORS = {
        "white", "red", "pink", "orange", "yellow", "green", "cyan", "blue", "purple", "black",
        "white2", "red2", "pink2", "orange2", "yellow2", "green2", "cyan2", "blue2", "purple2", "black2",
    }

    def _cmd_opcomment(self, arg: str):
        if not arg:
            return
        if arg.strip().lower() == "delete":
            self._opcomment_delete()
            return

        text = arg.strip()
        color = ""
        is_permanent = False

        # /color や /perm コマンドをパース
        # 例: "/yellow /perm テキスト" → color=yellow, permanent=True, text="テキスト"
        while text.startswith("/"):
            parts = text.split(None, 1)
            cmd = parts[0][1:].lower()  # "/" を除去
            if cmd in self._OPCOMMENT_COLORS:
                color = cmd
                text = parts[1] if len(parts) > 1 else ""
            elif cmd in ("perm", "permanent", "fixed"):
                is_permanent = True
                text = parts[1] if len(parts) > 1 else ""
            else:
                break  # 不明なコマンドはテキストの一部

        if not text:
            return
        self._opcomment_send(text, color=color, is_permanent=is_permanent)

    def _opcomment_send(self, text: str, *, color: str = "", is_permanent: bool = False):
        def _run():
            loop = asyncio.new_event_loop()
            try:
                from _niconico.broadcaster_api import BroadcasterAPI
                session = loop.run_until_complete(self._create_auth_session())
                api = BroadcasterAPI(session)
                ok = loop.run_until_complete(
                    api.send_operator_comment(self._program_id, text, color=color, is_permanent=is_permanent)
                )
                loop.run_until_complete(session.close())
                if ok and self.plugin_queue:
                    self.send_text(self.plugin_queue, _t("opcomment_sent_cue", text=text[:50]))
            finally:
                loop.close()

        threading.Thread(target=_run, daemon=True).start()

    def _opcomment_delete(self):
        def _run():
            loop = asyncio.new_event_loop()
            try:
                from _niconico.broadcaster_api import BroadcasterAPI
                session = loop.run_until_complete(self._create_auth_session())
                api = BroadcasterAPI(session)
                loop.run_until_complete(api.delete_operator_comment(self._program_id))
                loop.run_until_complete(session.close())
            finally:
                loop.close()

        threading.Thread(target=_run, daemon=True).start()

    # ==========================================
    # ユーティリティ
    # ==========================================
    async def _create_auth_session(self) -> aiohttp.ClientSession:
        """認証済み aiohttp セッションを作成する (CMD用)"""
        from http.cookies import SimpleCookie
        settings = self.get_settings()
        session = aiohttp.ClientSession()
        user_session = settings.get("user_session", "")
        if user_session:
            c = SimpleCookie()
            c["user_session"] = user_session
            c["user_session"]["domain"] = ".nicovideo.jp"
            c["user_session"]["path"] = "/"
            session.cookie_jar.update_cookies(c)
        return session

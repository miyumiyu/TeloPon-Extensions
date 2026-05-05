"""
FirstTimerCounter v1.00 - 初見さんカウンター for TeloPon
==========================================================
配信中のコメントから「初見」「おはつ」などのキーワードを検出し、
初見視聴者の人数をステータスウィンドウに常時表示するプラグイン。

機能:
  - 設定したキーワードがコメントに含まれるとカウントアップ
  - 同一視聴者は1回のみカウント（重複防止）
  - カウント数を window-status に常時表示
  - キーワード編集UI、クリアボタン
  - JSON永続化（カウント値・既知ユーザー）
"""

import threading
import tkinter as tk
from tkinter import ttk

from plugin_manager import BasePlugin
import drawing
import logger


# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "✨ 初見さんカウンター",
        "panel_title": "✨ 初見さんカウンター 設定",
        "chk_enabled": "ON / OFF",
        "lf_keywords": " 検出キーワード（1行に1個） ",
        "label_count": "現在のカウント:",
        "label_known_users": "既知ユーザー数:",
        "btn_clear": "🗑️ カウンタークリア",
        "btn_close": "閉じる",
        "label_topic_text": "表示する見出し文字:",
        "label_help": "コメントに以下のキーワードが含まれると、\n同じ視聴者で重複しないようにカウントアップします。",
        "telop_topic": "✨ 初見さん",
        "telop_main_zero": "0人",
        "telop_main": "{count}人",
    },
    "en": {
        "plugin_name": "✨ First-Timer Counter",
        "panel_title": "✨ First-Timer Counter Settings",
        "chk_enabled": "ON / OFF",
        "lf_keywords": " Detection keywords (one per line) ",
        "label_count": "Current count:",
        "label_known_users": "Known users:",
        "btn_clear": "🗑️ Clear counter",
        "btn_close": "Close",
        "label_topic_text": "Header text:",
        "label_help": "Counts up when a comment contains these keywords.\nDuplicates from the same user are ignored.",
        "telop_topic": "✨ First-timers",
        "telop_main_zero": "0",
        "telop_main": "{count}",
    },
    "ko": {
        "plugin_name": "✨ 첫 방문자 카운터",
        "panel_title": "✨ 첫 방문자 카운터 설정",
        "chk_enabled": "ON / OFF",
        "lf_keywords": " 검출 키워드(한 줄에 하나) ",
        "label_count": "현재 카운트:",
        "label_known_users": "알려진 사용자 수:",
        "btn_clear": "🗑️ 카운터 클리어",
        "btn_close": "닫기",
        "label_topic_text": "표시 헤더 문자:",
        "label_help": "댓글에 이 키워드가 포함되면 카운트업합니다.\n같은 시청자는 중복되지 않습니다.",
        "telop_topic": "✨ 첫 방문",
        "telop_main_zero": "0명",
        "telop_main": "{count}명",
    },
    "ru": {
        "plugin_name": "✨ Счётчик новичков",
        "panel_title": "✨ Настройки счётчика новичков",
        "chk_enabled": "ВКЛ / ВЫКЛ",
        "lf_keywords": " Ключевые слова (по одному на строку) ",
        "label_count": "Текущий счёт:",
        "label_known_users": "Известных пользователей:",
        "btn_clear": "🗑️ Очистить счётчик",
        "btn_close": "Закрыть",
        "label_topic_text": "Заголовок:",
        "label_help": "Увеличивается, когда в комментарии есть ключевые слова.\nПовторы одного пользователя игнорируются.",
        "telop_topic": "✨ Новички",
        "telop_main_zero": "0",
        "telop_main": "{count}",
    },
}


def _t(key):
    try:
        import i18n
        lang = i18n.get_lang()
    except Exception:
        lang = "en"
    return _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))


class FirstTimerCounter(BasePlugin):
    PLUGIN_ID = "first_timer_counter"
    PLUGIN_NAME = "First-Timer Counter"
    PLUGIN_VERSION = "1.00"
    PLUGIN_TYPE = "TOOL"

    DEFAULT_KEYWORDS = ["初見", "おはつ", "はじめまして", "初コメ", "first time", "新人"]

    def __init__(self):
        super().__init__()
        self._panel = None
        self._lock = threading.Lock()

        saved = self.get_settings()
        self._enabled = bool(saved.get("enabled", False))
        self._keywords = list(saved.get("keywords", self.DEFAULT_KEYWORDS))
        self._count = int(saved.get("count", 0))
        self._known_users = set(saved.get("known_users", []))
        # 見出し文字（空の場合はi18nデフォルトを使う）
        self._topic_text = str(saved.get("topic_text", ""))

        # UIラベル参照（カウント変動時に更新）
        self._lbl_count_var = None
        self._lbl_known_var = None

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "keywords": list(self.DEFAULT_KEYWORDS),
            "count": 0,
            "known_users": [],
            "topic_text": "",  # 空ならi18nデフォルト（"✨ 初見さん"等）
        }

    # --------------------------------------------------------
    # ライブ開始/停止
    # --------------------------------------------------------
    def start(self, prompt_config, message_queue):
        """ライブ開始時にステータスウィンドウを表示"""
        if self._enabled:
            self._refresh_status_window()

    def stop(self):
        """ライブ停止時はクリアしない（カウンタは継続。次回起動でも表示）"""
        pass

    # --------------------------------------------------------
    # コメント受信フック
    # --------------------------------------------------------
    def on_comment_received(self, text, author, source):
        if not self._enabled:
            return
        if not text or not author:
            return

        with self._lock:
            # 重複チェック（同じ著者は1回のみ）
            if author in self._known_users:
                return

            # キーワードマッチ（大文字小文字無視）
            text_lower = text.lower()
            matched = any(kw.lower() in text_lower for kw in self._keywords if kw.strip())
            if not matched:
                return

            # カウントアップ + 既知ユーザー登録
            self._count += 1
            self._known_users.add(author)
            new_count = self._count
            known_n = len(self._known_users)

        logger.info(f"[FirstTimerCounter] ✨ 初見さん検出: {author} → {new_count}人")
        self._save_state()
        self._refresh_status_window()
        self._update_ui_labels(new_count, known_n)

    # --------------------------------------------------------
    # ステータスウィンドウ更新
    # --------------------------------------------------------
    def _refresh_status_window(self):
        # ユーザー設定の見出し文字優先、空ならi18nデフォルト
        topic = self._topic_text.strip() if self._topic_text else _t("telop_topic")
        if self._count == 0:
            main = _t("telop_main_zero")
        else:
            main = _t("telop_main").replace("{count}", str(self._count))
        try:
            drawing.force_show_telop("status", topic, main, "window-status", "layout-flat", "NONE", 0)
        except Exception as e:
            logger.warning(f"[FirstTimerCounter] ステータス更新エラー: {e}")

    # --------------------------------------------------------
    # 永続化
    # --------------------------------------------------------
    def _save_state(self):
        settings = self.get_settings()
        settings["enabled"] = self._enabled
        settings["keywords"] = list(self._keywords)
        settings["count"] = int(self._count)
        settings["known_users"] = list(self._known_users)
        settings["topic_text"] = self._topic_text
        self.save_settings(settings)

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("panel_title"))
        self._panel.geometry("420x560")
        self._panel.minsize(380, 520)
        self._panel.attributes("-topmost", True)

        main_f = ttk.Frame(self._panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # ON/OFF
        self._var_enabled = tk.BooleanVar(value=self._enabled)
        def _on_enabled(*_):
            self._enabled = bool(self._var_enabled.get())
            self._save_state()
            if self._enabled:
                self._refresh_status_window()
            else:
                drawing.clear_group("status")
        self._var_enabled.trace_add("write", _on_enabled)
        ttk.Checkbutton(main_f, text=_t("chk_enabled"), variable=self._var_enabled).pack(anchor="w", pady=(0, 10))

        # 見出し文字（topic）入力
        topic_f = ttk.Frame(main_f)
        topic_f.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(topic_f, text=_t("label_topic_text")).pack(anchor="w")
        # 表示時のデフォルト=ユーザー指定があればそれ、空ならi18nデフォルトをplaceholder的に表示
        initial_topic = self._topic_text if self._topic_text else _t("telop_topic")
        self._var_topic_text = tk.StringVar(value=initial_topic)
        ent_topic = ttk.Entry(topic_f, textvariable=self._var_topic_text)
        ent_topic.pack(fill=tk.X, pady=(2, 0))

        def _on_topic_changed(*_):
            new_text = self._var_topic_text.get()
            # i18nデフォルトと一致 or 空 ならカスタム指定なし扱い（空保存）
            self._topic_text = "" if (not new_text.strip() or new_text == _t("telop_topic")) else new_text
            self._save_state()
            if self._enabled:
                self._refresh_status_window()
        self._var_topic_text.trace_add("write", _on_topic_changed)

        # 説明
        ttk.Label(main_f, text=_t("label_help"), foreground="gray", justify="left").pack(anchor="w", pady=(0, 8))

        # キーワード編集
        lf = ttk.LabelFrame(main_f, text=_t("lf_keywords"), padding=10)
        lf.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self._txt_keywords = tk.Text(lf, height=8, font=("", 10))
        self._txt_keywords.pack(fill=tk.BOTH, expand=True)
        self._txt_keywords.insert("1.0", "\n".join(self._keywords))

        def _on_kw_changed(*_):
            txt = self._txt_keywords.get("1.0", "end-1c")
            self._keywords = [line.strip() for line in txt.splitlines() if line.strip()]
            self._save_state()
        self._txt_keywords.bind("<FocusOut>", _on_kw_changed)
        self._txt_keywords.bind("<KeyRelease>", _on_kw_changed)

        # 状態表示
        status_f = ttk.Frame(main_f)
        status_f.pack(fill=tk.X, pady=(0, 5))

        self._lbl_count_var = tk.StringVar(value=f"{_t('label_count')} {self._count}")
        ttk.Label(status_f, textvariable=self._lbl_count_var, font=("", 11, "bold")).pack(anchor="w")

        self._lbl_known_var = tk.StringVar(value=f"{_t('label_known_users')} {len(self._known_users)}")
        ttk.Label(status_f, textvariable=self._lbl_known_var, foreground="gray").pack(anchor="w")

        # クリアボタン
        tk.Button(main_f, text=_t("btn_clear"), bg="#ff8888", fg="white",
                  font=("", 10, "bold"), command=self._clear_counter).pack(fill=tk.X, pady=(8, 5))

        # 閉じるボタン
        tk.Button(main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
                  font=("", 10, "bold"), command=self._save_and_close).pack(fill=tk.X)

        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

    def _clear_counter(self):
        with self._lock:
            self._count = 0
            self._known_users.clear()
        self._save_state()
        self._update_ui_labels(0, 0)
        if self._enabled:
            self._refresh_status_window()
        logger.info("[FirstTimerCounter] 🗑️ カウンタークリア")

    def _update_ui_labels(self, count, known_n):
        """UIのラベルをスレッドセーフに更新"""
        if not self._panel or not self._panel.winfo_exists():
            return
        try:
            if self._lbl_count_var:
                self._panel.after(0, lambda c=count: self._lbl_count_var.set(f"{_t('label_count')} {c}") if self._panel and self._panel.winfo_exists() else None)
            if self._lbl_known_var:
                self._panel.after(0, lambda n=known_n: self._lbl_known_var.set(f"{_t('label_known_users')} {n}") if self._panel and self._panel.winfo_exists() else None)
        except Exception:
            pass

    def _save_and_close(self):
        # キーワードの最終確定
        try:
            txt = self._txt_keywords.get("1.0", "end-1c")
            self._keywords = [line.strip() for line in txt.splitlines() if line.strip()]
        except Exception:
            pass
        self._save_state()
        self._panel.destroy()

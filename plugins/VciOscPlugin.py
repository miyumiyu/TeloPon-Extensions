"""
VciOscPlugin v1.01 - VirtualCast VCI OSC テロップ送信プラグイン

AIが出力したテロップを OSC (OpenSound Control) 経由で
VirtualCast の VCI に送信します。

必要環境:
  - python-osc ライブラリ（pip install python-osc）
  - VirtualCast でOSC受信機能を有効化（ポート19100）
  - テロップ表示用の VCI がVirtualCast上に配置されていること
"""

import re
import tkinter as tk
from tkinter import ttk
from plugin_manager import BasePlugin

import logger

try:
    from pythonosc.udp_client import SimpleUDPClient
except ImportError:
    SimpleUDPClient = None

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "VCI OSC テロップ",
        "panel_title": "🎮 VCI OSC テロップ設定",
        "lf_conn": " OSC接続設定 ",
        "label_ip": "送信先IP:",
        "label_port": "送信先ポート:",
        "label_address": "OSCアドレス:",
        "btn_test": "テスト送信",
        "test_ok": "✅ 送信しました",
        "test_fail": "❌ 送信失敗",
        "lf_content": " 送信内容設定 ",
        "label_send_topic": "📌 TOPICも送信する",
        "label_send_badge": "🏷️ バッジも送信する",
        "label_format": "送信フォーマット:",
        "format_main_only": "MAINのみ",
        "format_topic_main": "TOPIC | MAIN",
        "format_json": "JSON形式",
        "btn_close": "閉じる",
        "warn_no_lib": "python-oscライブラリが見つかりません（pip install python-osc）",
    },
    "en": {
        "plugin_name": "VCI OSC Telop",
        "panel_title": "🎮 VCI OSC Telop Settings",
        "lf_conn": " OSC Connection ",
        "label_ip": "Target IP:",
        "label_port": "Target Port:",
        "label_address": "OSC Address:",
        "btn_test": "Test Send",
        "test_ok": "✅ Sent",
        "test_fail": "❌ Send failed",
        "lf_content": " Content Settings ",
        "label_send_topic": "📌 Send TOPIC",
        "label_send_badge": "🏷️ Send Badge",
        "label_format": "Send Format:",
        "format_main_only": "MAIN only",
        "format_topic_main": "TOPIC | MAIN",
        "format_json": "JSON format",
        "btn_close": "Close",
        "warn_no_lib": "python-osc library not found (pip install python-osc)",
    },
    "ko": {
        "plugin_name": "VCI OSC 텔롭",
        "panel_title": "🎮 VCI OSC 텔롭 설정",
        "lf_conn": " OSC 연결 설정 ",
        "label_ip": "대상 IP:",
        "label_port": "대상 포트:",
        "label_address": "OSC 주소:",
        "btn_test": "테스트 전송",
        "test_ok": "✅ 전송 완료",
        "test_fail": "❌ 전송 실패",
        "lf_content": " 전송 내용 설정 ",
        "label_send_topic": "📌 TOPIC도 전송",
        "label_send_badge": "🏷️ 배지도 전송",
        "label_format": "전송 형식:",
        "format_main_only": "MAIN만",
        "format_topic_main": "TOPIC | MAIN",
        "format_json": "JSON 형식",
        "btn_close": "닫기",
        "warn_no_lib": "python-osc 라이브러리를 찾을 수 없습니다 (pip install python-osc)",
    },
    "ru": {
        "plugin_name": "VCI OSC телоп",
        "panel_title": "🎮 Настройки VCI OSC",
        "lf_conn": " Подключение OSC ",
        "label_ip": "IP-адрес:",
        "label_port": "Порт:",
        "label_address": "OSC-адрес:",
        "btn_test": "Тест отправки",
        "test_ok": "✅ Отправлено",
        "test_fail": "❌ Ошибка отправки",
        "lf_content": " Настройки содержания ",
        "label_send_topic": "📌 Отправлять TOPIC",
        "label_send_badge": "🏷️ Отправлять значок",
        "label_format": "Формат:",
        "format_main_only": "Только MAIN",
        "format_topic_main": "TOPIC | MAIN",
        "format_json": "Формат JSON",
        "btn_close": "Закрыть",
        "warn_no_lib": "Библиотека python-osc не найдена (pip install python-osc)",
    },
}

def _t(key):
    try:
        import i18n
        lang = getattr(i18n, '_current_language', 'en') or 'en'
        lang = lang[:2]
    except Exception:
        lang = "en"
    return _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))


def _strip_tags(text):
    if not text:
        return ""
    text = re.sub(r'\[/?b[12]\]', '', text)
    text = re.sub(r'</?b[012]>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


class VciOscPlugin(BasePlugin):
    PLUGIN_ID   = "vci_osc"
    PLUGIN_NAME = "VCI OSC Telop"
    PLUGIN_VERSION = "1.01"
    PLUGIN_TYPE = "TOOL"

    def __init__(self):
        super().__init__()
        self._panel = None
        self._client = None

        saved = self.get_settings()
        self._live_enabled    = saved.get("enabled", False)
        self._live_ip         = saved.get("ip", "127.0.0.1")
        self._live_port       = int(saved.get("port", 19100))
        self._live_address    = saved.get("osc_address", "/telopon/telop/text")
        self._live_send_topic = saved.get("send_topic", True)
        self._live_send_badge = saved.get("send_badge", False)
        self.is_running = self._live_enabled

        if SimpleUDPClient is None:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('warn_no_lib')}")
        elif self._live_enabled:
            self._connect()

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "ip": "127.0.0.1",
            "port": 19100,
            "osc_address": "/telopon/telop/text",
            "send_topic": True,
            "send_badge": False,
        }

    def start(self, prompt_config, message_queue):
        pass

    def stop(self):
        pass

    def _connect(self):
        try:
            self._client = SimpleUDPClient(self._live_ip, self._live_port)
            logger.info(f"[{self.PLUGIN_NAME}] OSC接続: {self._live_ip}:{self._live_port}")
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] OSC接続失敗: {e}")
            self._client = None

    # --------------------------------------------------------
    # テロップ出力フック
    # --------------------------------------------------------
    def on_telop_output(self, topic, main, window, layout, badge):
        if not self._live_enabled or not self._client or not main:
            return

        clean_main = _strip_tags(main)
        if not clean_main:
            return

        clean_topic = _strip_tags(topic) if topic else ""
        clean_badge = badge if badge and badge != "NONE" else ""

        # 送信テキスト構築
        parts = []
        if self._live_send_topic and clean_topic:
            parts.append(clean_topic)
        parts.append(clean_main)
        text = " | ".join(parts)

        try:
            # メインテキスト送信（VCI側のUTF-8認識問題を回避するためbytesで送信）
            self._client.send_message(self._live_address, text.encode("utf-8"))

            # バッジを別アドレスで送信（オプション）
            if self._live_send_badge and clean_badge:
                self._client.send_message(self._live_address + "/badge", clean_badge.encode("utf-8"))

            # ウィンドウ種類を別アドレスで送信
            self._client.send_message(self._live_address + "/window", window.encode("utf-8"))

            logger.debug(f"[{self.PLUGIN_NAME}] OSC送信: {text[:50]}")
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] OSC送信エラー: {e}")

    # --------------------------------------------------------
    # 設定 UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("panel_title"))
        self._panel.geometry("400x420")
        self._panel.minsize(380, 400)
        self._panel.attributes("-topmost", True)

        settings = self.get_settings()
        main_f = ttk.Frame(self._panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # --- ON/OFF ---
        self._var_enabled = tk.BooleanVar(value=self._live_enabled)
        def _on_enabled(*_):
            self._live_enabled = self._var_enabled.get()
            self.is_running = self._live_enabled
            if self._live_enabled and not self._client:
                self._connect()
        self._var_enabled.trace_add("write", _on_enabled)
        ttk.Checkbutton(main_f, text="OSC送信 ON", variable=self._var_enabled).pack(anchor="w", pady=(0, 8))

        # --- 接続設定 ---
        lf_conn = ttk.LabelFrame(main_f, text=_t("lf_conn"), padding=10)
        lf_conn.pack(fill=tk.X, pady=(0, 10))

        row_ip = ttk.Frame(lf_conn)
        row_ip.pack(fill=tk.X, pady=2)
        ttk.Label(row_ip, text=_t("label_ip"), width=14).pack(side=tk.LEFT)
        self._ent_ip = ttk.Entry(row_ip, width=18)
        self._ent_ip.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._ent_ip.insert(0, settings.get("ip", "127.0.0.1"))

        row_port = ttk.Frame(lf_conn)
        row_port.pack(fill=tk.X, pady=2)
        ttk.Label(row_port, text=_t("label_port"), width=14).pack(side=tk.LEFT)
        self._ent_port = ttk.Entry(row_port, width=8)
        self._ent_port.pack(side=tk.LEFT)
        self._ent_port.insert(0, str(settings.get("port", 19100)))

        row_addr = ttk.Frame(lf_conn)
        row_addr.pack(fill=tk.X, pady=2)
        ttk.Label(row_addr, text=_t("label_address"), width=14).pack(side=tk.LEFT)
        self._ent_addr = ttk.Entry(row_addr, width=24)
        self._ent_addr.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._ent_addr.insert(0, settings.get("osc_address", "/telopon/telop/text"))

        self._lbl_test = ttk.Label(lf_conn, text="")
        self._lbl_test.pack(anchor="w", pady=(4, 0))

        tk.Button(lf_conn, text=_t("btn_test"), bg="#17a2b8", fg="white",
                  command=self._test_send).pack(fill=tk.X, pady=(4, 0))

        # --- 送信内容設定 ---
        lf_content = ttk.LabelFrame(main_f, text=_t("lf_content"), padding=10)
        lf_content.pack(fill=tk.X, pady=(0, 10))

        self._var_topic = tk.BooleanVar(value=self._live_send_topic)
        def _on_topic(*_):
            self._live_send_topic = self._var_topic.get()
        self._var_topic.trace_add("write", _on_topic)
        ttk.Checkbutton(lf_content, text=_t("label_send_topic"),
                         variable=self._var_topic).pack(anchor="w", pady=2)

        self._var_badge = tk.BooleanVar(value=self._live_send_badge)
        def _on_badge(*_):
            self._live_send_badge = self._var_badge.get()
        self._var_badge.trace_add("write", _on_badge)
        ttk.Checkbutton(lf_content, text=_t("label_send_badge"),
                         variable=self._var_badge).pack(anchor="w", pady=2)

        # --- 閉じるボタン ---
        tk.Button(main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
                  font=("", 10, "bold"), command=self._save_and_close).pack(fill=tk.X, pady=(10, 0))
        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

    def _test_send(self):
        """テスト送信"""
        if SimpleUDPClient is None:
            self._lbl_test.config(text=f"{_t('test_fail')}: python-osc not installed", foreground="red")
            return
        try:
            ip = self._ent_ip.get().strip()
            port = int(self._ent_port.get().strip())
            addr = self._ent_addr.get().strip()
            client = SimpleUDPClient(ip, port)
            client.send_message(addr, "TeloPon OSC Test Message / テスト送信".encode("utf-8"))
            self._lbl_test.config(text=_t("test_ok"), foreground="green")
            logger.info(f"[{self.PLUGIN_NAME}] テスト送信成功: {ip}:{port} {addr}")
        except Exception as e:
            self._lbl_test.config(text=f"{_t('test_fail')}: {e}", foreground="red")
            logger.warning(f"[{self.PLUGIN_NAME}] テスト送信失敗: {e}")

    def _save_and_close(self):
        settings = self.get_settings()
        settings["enabled"]     = self._live_enabled
        settings["ip"]          = self._ent_ip.get().strip()
        settings["port"]        = int(self._ent_port.get().strip())
        settings["osc_address"] = self._ent_addr.get().strip()
        settings["send_topic"]  = self._live_send_topic
        settings["send_badge"]  = self._live_send_badge
        self.save_settings(settings)

        # 設定反映
        self._live_ip      = settings["ip"]
        self._live_port    = settings["port"]
        self._live_address = settings["osc_address"]
        if self._live_enabled:
            self._connect()

        logger.info(f"[{self.PLUGIN_NAME}] 設定を保存: {settings['ip']}:{settings['port']} {settings['osc_address']}")
        self._panel.destroy()

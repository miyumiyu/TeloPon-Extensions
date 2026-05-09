"""
TeloponBridge v1.00 - 2つのTeloPonを会話させるプラグイン
=============================================================
TeloPonインスタンスAとBをHTTPで連携し、お互いのAIが会話する仕組み。

機能:
  - 自身のテロップ出力を捕捉して、相手インスタンスの受信エンドポイントへ送信
  - 自身もHTTPサーバーを起動し、相手のメッセージを受信したらAIへテキスト注入
  - 受信したメッセージは "[ブリッジ] {speaker}さん: {内容}" 形式でAIに届く
  - 暴走防止: 最低送信間隔 + 最大ターン数の自動停止
  - 手動の一時停止／再開／ターンリセット

使い方:
  1. 2つのTeloPonインスタンスを別フォルダから起動（settings.json競合防止）
  2. 各インスタンスでこのプラグインを有効化
  3. インスタンスA: recv_port=9001, send_url=http://localhost:9002/recv, speaker_name="AI-A"
     インスタンスB: recv_port=9002, send_url=http://localhost:9001/recv, speaker_name="AI-B"
  4. 配信開始 → 配信者が「Bさん、こんにちは」のように話しかけ → AI同士の会話が始まる
"""

import json
import threading
import time
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk
from http.server import HTTPServer, BaseHTTPRequestHandler

from plugin_manager import BasePlugin
import logger


# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "🌉 TeloPon ブリッジ",
        "panel_title": "🌉 TeloPon ブリッジ 設定",
        "chk_enabled": "ブリッジ起動 (ON / OFF)",
        "lf_network": "ネットワーク設定",
        "label_recv_port": "受信ポート（自分が listen）",
        "label_send_url": "送信先URL（相手の受信エンドポイント）",
        "label_speaker": "自分の名前（送信時に付与）",
        "lf_loop_control": "ループ制御",
        "label_min_interval": "最低送信間隔（秒）",
        "label_max_turns": "最大ターン数（0=無制限）",
        "lf_status": "状態",
        "label_server": "受信サーバー:",
        "label_sent": "送信回数:",
        "label_recv": "受信回数:",
        "label_turn": "ターン数:",
        "label_paused": "一時停止中",
        "btn_pause": "⏸ 一時停止",
        "btn_resume": "▶ 再開",
        "btn_reset_turn": "🔄 ターンリセット",
        "btn_close": "閉じる",
        "status_running": "✅ 稼働中",
        "status_stopped": "⏹ 停止中",
        "status_paused": "⏸ 一時停止中",
        "help": "2つのTeloPonをHTTP連携で会話させます。\n配信者の発話で会話の方向を誘導してください。",
        "prompt_addon": (
            "\n# 【TeloPonブリッジ】\n"
            "別のAIから「[ブリッジ] {speaker}さん: 〜」形式でメッセージが届きます（{speaker} は相手のAIキャラクター名）。\n"
            "これは別のTeloPonインスタンスで動作している別のAIキャラクターからの発言です。\n"
            "視聴者コメントとは別物として扱い、会話相手として自然に応答してください。\n"
            "相手の名前を呼んで返事すると会話が自然になります（例：「{speaker}さん、それは...」）。\n"
            "返答は短めに（2〜3文以内）。長い独白を避け、相手にターンを渡す意識で話してください。\n"
        ),
    },
    "en": {
        "plugin_name": "🌉 TeloPon Bridge",
        "panel_title": "🌉 TeloPon Bridge Settings",
        "chk_enabled": "Activate Bridge (ON / OFF)",
        "lf_network": "Network Settings",
        "label_recv_port": "Receive port (this instance listens)",
        "label_send_url": "Send URL (other instance's receive endpoint)",
        "label_speaker": "Speaker name (added when sending)",
        "lf_loop_control": "Loop Control",
        "label_min_interval": "Min send interval (sec)",
        "label_max_turns": "Max turns (0 = unlimited)",
        "lf_status": "Status",
        "label_server": "Receive server:",
        "label_sent": "Sent count:",
        "label_recv": "Received count:",
        "label_turn": "Turns:",
        "label_paused": "Paused",
        "btn_pause": "⏸ Pause",
        "btn_resume": "▶ Resume",
        "btn_reset_turn": "🔄 Reset turns",
        "btn_close": "Close",
        "status_running": "✅ Running",
        "status_stopped": "⏹ Stopped",
        "status_paused": "⏸ Paused",
        "help": "Bridges two TeloPon instances via HTTP for AI conversation.\nGuide the dialogue with your voice.",
        "prompt_addon": (
            "\n# [TeloPon Bridge]\n"
            "Messages from another AI may arrive in the format: '[Bridge] {speaker}: ...' ({speaker} is the other AI's character name).\n"
            "This is another AI character running in a separate TeloPon instance.\n"
            "Treat them as a conversation partner (not a viewer comment) and respond naturally.\n"
            "Address them by name in your reply (e.g., '{speaker}, that's...') to make the conversation flow naturally.\n"
            "Keep replies short (2-3 sentences). Avoid long monologues and pass the turn back.\n"
        ),
    },
    "ko": {
        "plugin_name": "🌉 TeloPon 브릿지",
        "panel_title": "🌉 TeloPon 브릿지 설정",
        "chk_enabled": "브릿지 활성화 (ON / OFF)",
        "lf_network": "네트워크 설정",
        "label_recv_port": "수신 포트 (이 인스턴스가 listen)",
        "label_send_url": "송신 URL (상대 인스턴스의 수신 엔드포인트)",
        "label_speaker": "본인 이름 (송신 시 부여)",
        "lf_loop_control": "루프 제어",
        "label_min_interval": "최소 송신 간격 (초)",
        "label_max_turns": "최대 턴 수 (0 = 무제한)",
        "lf_status": "상태",
        "label_server": "수신 서버:",
        "label_sent": "송신 횟수:",
        "label_recv": "수신 횟수:",
        "label_turn": "턴 수:",
        "label_paused": "일시 중지 중",
        "btn_pause": "⏸ 일시 중지",
        "btn_resume": "▶ 재개",
        "btn_reset_turn": "🔄 턴 리셋",
        "btn_close": "닫기",
        "status_running": "✅ 작동 중",
        "status_stopped": "⏹ 중지됨",
        "status_paused": "⏸ 일시 중지",
        "help": "2개의 TeloPon을 HTTP로 연결하여 AI끼리 대화시킵니다.\n방송자의 발화로 대화 방향을 유도해 주세요.",
        "prompt_addon": (
            "\n# [TeloPon 브릿지]\n"
            "다른 AI로부터 '[브릿지] {speaker}님: ~' 형식의 메시지가 도착합니다 ({speaker}는 상대 AI 캐릭터의 이름).\n"
            "다른 TeloPon 인스턴스에서 동작 중인 다른 AI 캐릭터의 발언입니다.\n"
            "시청자 댓글과는 다르게 취급하고, 대화 상대로 자연스럽게 응답해 주세요.\n"
            "상대의 이름을 부르며 답하면 대화가 자연스러워집니다 (예: '{speaker}님, 그건...').\n"
            "답변은 짧게 (2~3문장 이내). 긴 독백을 피하고 턴을 넘기는 의식으로 대화하세요.\n"
        ),
    },
    "ru": {
        "plugin_name": "🌉 Мост TeloPon",
        "panel_title": "🌉 Настройки моста TeloPon",
        "chk_enabled": "Активировать мост (ВКЛ / ВЫКЛ)",
        "lf_network": "Сетевые настройки",
        "label_recv_port": "Порт приёма (этот экземпляр слушает)",
        "label_send_url": "URL отправки (точка приёма другого экземпляра)",
        "label_speaker": "Своё имя (добавляется при отправке)",
        "lf_loop_control": "Контроль цикла",
        "label_min_interval": "Мин. интервал отправки (сек)",
        "label_max_turns": "Макс. ходов (0 = без ограничения)",
        "lf_status": "Состояние",
        "label_server": "Сервер приёма:",
        "label_sent": "Отправлено:",
        "label_recv": "Получено:",
        "label_turn": "Ходов:",
        "label_paused": "На паузе",
        "btn_pause": "⏸ Пауза",
        "btn_resume": "▶ Возобновить",
        "btn_reset_turn": "🔄 Сбросить ходы",
        "btn_close": "Закрыть",
        "status_running": "✅ Работает",
        "status_stopped": "⏹ Остановлен",
        "status_paused": "⏸ На паузе",
        "help": "Связывает два экземпляра TeloPon через HTTP для разговора ИИ.\nВедите диалог своим голосом.",
        "prompt_addon": (
            "\n# [Мост TeloPon]\n"
            "Сообщения от другого ИИ могут приходить в формате: '[Мост] {speaker}: ...' ({speaker} — имя другого ИИ-персонажа).\n"
            "Это другой персонаж ИИ, работающий в отдельном экземпляре TeloPon.\n"
            "Обращайтесь с ними как с собеседником (а не комментарием зрителя) и отвечайте естественно.\n"
            "Обращайтесь к ним по имени в ответе (например, '{speaker}, это...'), чтобы разговор шёл естественно.\n"
            "Отвечайте кратко (2-3 предложения). Избегайте длинных монологов и передавайте ход обратно.\n"
        ),
    },
}


def _t(key):
    try:
        import i18n
        lang = i18n.get_lang()
    except Exception:
        lang = "en"
    return _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))


# ==========================================
# HTTP受信ハンドラ（プラグインインスタンス参照を持つ）
# ==========================================
class _BridgeHandler(BaseHTTPRequestHandler):
    plugin_ref = None  # クラス変数：プラグインインスタンスへの参照

    def do_POST(self):
        if self.path != "/recv":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 100_000:  # 100KB上限
                self.send_error(400, "Invalid length")
                return
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            if self.plugin_ref:
                self.plugin_ref._on_recv(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as e:
            logger.warning(f"[TeloponBridge] 受信エラー: {e}")
            try:
                self.send_error(500)
            except Exception:
                pass

    def log_message(self, format, *args):
        # アクセスログを抑制（標準エラーへの吐き出しをやめる）
        pass


# ==========================================
# プラグイン本体
# ==========================================
class TeloponBridge(BasePlugin):
    PLUGIN_ID = "telopon_bridge"
    PLUGIN_NAME = "TeloPon Bridge"
    PLUGIN_VERSION = "1.00"
    PLUGIN_TYPE = "TOOL"

    def __init__(self):
        super().__init__()
        self._panel = None
        self._lock = threading.Lock()
        self._server = None
        self._server_thread = None

        saved = self.get_settings()
        self._enabled = bool(saved.get("enabled", False))
        self._paused = False  # 手動一時停止
        self._recv_port = int(saved.get("recv_port", 9001))
        self._send_url = str(saved.get("send_url", "http://localhost:9002/recv"))
        self._speaker_name = str(saved.get("speaker_name", "AI-A"))
        self._min_interval_sec = float(saved.get("min_interval_sec", 5.0))
        self._max_turns = int(saved.get("max_turns", 0))  # 0 = 無制限

        # AI名（ライブ開始時に prompt_config から取得）
        self._ai_name = ""

        # ランタイム状態
        self._last_send_time = 0.0
        self._sent_count = 0
        self._recv_count = 0
        self._turn_count = 0

        # is_connected: ライブ接続前でも enabled だけでアクティブにしたいので未定義
        # 設定の enabled でバッジが制御される

        # UI参照
        self._var_enabled = None
        self._var_recv_port = None
        self._var_send_url = None
        self._var_speaker = None
        self._var_min_interval = None
        self._var_max_turns = None
        self._lbl_server_var = None
        self._lbl_sent_var = None
        self._lbl_recv_var = None
        self._lbl_turn_var = None
        self._btn_pause = None

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "recv_port": 9001,
            "send_url": "http://localhost:9002/recv",
            "speaker_name": "AI-A",
            "min_interval_sec": 5.0,
            "max_turns": 0,
        }

    def get_prompt_addon(self):
        if self._enabled:
            return _t("prompt_addon")
        return ""

    # --------------------------------------------------------
    # ライフサイクル
    # --------------------------------------------------------
    def start(self, prompt_config, plugin_queue):
        self.plugin_queue = plugin_queue
        # AI名をプロンプト設定から取得（例: "テロぽん", "ナンシー"等）
        self._ai_name = str(prompt_config.get("ai_name", "")) if prompt_config else ""
        if self._ai_name:
            logger.info(f"[TeloponBridge] AI名を取得: {self._ai_name}")
        if self._enabled:
            self._start_server()

    def stop(self):
        self._stop_server()
        self.plugin_queue = None

    # --------------------------------------------------------
    # テロップ出力フック → 相手に送信
    # --------------------------------------------------------
    def on_telop_output(self, topic, main, window, layout, badge):
        if not self._enabled or self._paused:
            return
        if not main or not main.strip():
            return

        # ループ制御: 最低送信間隔
        now = time.time()
        if now - self._last_send_time < self._min_interval_sec:
            logger.debug(f"[TeloponBridge] スキップ（最低間隔 {self._min_interval_sec}s 未満）")
            return

        # ループ制御: 最大ターン数
        if self._max_turns > 0 and self._turn_count >= self._max_turns:
            logger.info(f"[TeloponBridge] 最大ターン数 {self._max_turns} 到達のため自動一時停止")
            self._paused = True
            self._update_ui()
            return

        # 別スレッドで送信（fire-and-forget）
        threading.Thread(
            target=self._do_send,
            args=(topic, main),
            daemon=True
        ).start()
        self._last_send_time = now

    def _do_send(self, topic, main):
        try:
            payload = json.dumps({
                "speaker": self._speaker_name,
                "ai_name": self._ai_name,  # プロンプトから取得したAIキャラ名
                "topic": topic or "",
                "main": main or "",
            }).encode("utf-8")

            req = urllib.request.Request(
                self._send_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                resp.read()
            self._sent_count += 1
            self._turn_count += 1
            self._update_ui_safe()
            logger.info(f"[TeloponBridge] 📤 送信成功: {self._send_url} ({len(main)}文字)")
        except urllib.error.URLError as e:
            logger.warning(f"[TeloponBridge] ❌ 送信失敗（接続エラー）: {e}")
        except Exception as e:
            logger.warning(f"[TeloponBridge] ❌ 送信失敗: {e}")

    # --------------------------------------------------------
    # 受信処理
    # --------------------------------------------------------
    def _on_recv(self, data):
        if not self._enabled or self._paused:
            return
        if not self.plugin_queue:
            logger.warning("[TeloponBridge] 受信したがライブ未接続のため破棄")
            return

        speaker = str(data.get("speaker", "?"))[:50]
        ai_name = str(data.get("ai_name", ""))[:50]
        main = str(data.get("main", ""))[:500]
        if not main.strip():
            return

        # 表示名: AI名があれば優先（例: "テロぽん"）、無ければ speaker（例: "AI-A"）
        # AI名と speaker が異なる場合は両方表示（例: "テロぽん (AI-A)"）
        if ai_name and ai_name != speaker:
            display_name = f"{ai_name} ({speaker})"
        elif ai_name:
            display_name = ai_name
        else:
            display_name = speaker

        text = f"[ブリッジ] {display_name}さん: {main}"
        self.send_text(self.plugin_queue, text)

        self._recv_count += 1
        self._turn_count += 1
        self._update_ui_safe()
        logger.info(f"[TeloponBridge] 📥 受信: {display_name} ({len(main)}文字)")

    # --------------------------------------------------------
    # HTTPサーバー管理
    # --------------------------------------------------------
    def _start_server(self):
        if self._server is not None:
            return  # 既に起動中

        try:
            handler = _BridgeHandler
            handler.plugin_ref = self
            self._server = HTTPServer(("127.0.0.1", self._recv_port), handler)
            self._server_thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True
            )
            self._server_thread.start()
            logger.info(f"[TeloponBridge] 🌉 受信サーバー起動: http://127.0.0.1:{self._recv_port}/recv")
        except OSError as e:
            logger.error(f"[TeloponBridge] ❌ サーバー起動失敗（ポート {self._recv_port}）: {e}")
            self._server = None
            self._server_thread = None

    def _stop_server(self):
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception as e:
                logger.warning(f"[TeloponBridge] サーバー停止エラー: {e}")
            self._server = None
            self._server_thread = None
            logger.info("[TeloponBridge] 🌉 受信サーバー停止")

    # --------------------------------------------------------
    # 永続化
    # --------------------------------------------------------
    def _save_state(self):
        s = self.get_settings()
        s["enabled"] = self._enabled
        s["recv_port"] = self._recv_port
        s["send_url"] = self._send_url
        s["speaker_name"] = self._speaker_name
        s["min_interval_sec"] = self._min_interval_sec
        s["max_turns"] = self._max_turns
        self.save_settings(s)

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("panel_title"))
        self._panel.geometry("460x600")
        self._panel.minsize(420, 560)
        self._panel.attributes("-topmost", True)

        main_f = ttk.Frame(self._panel, padding=12)
        main_f.pack(fill=tk.BOTH, expand=True)

        # ヘルプ
        ttk.Label(main_f, text=_t("help"), foreground="gray", justify="left").pack(anchor="w", pady=(0, 8))

        # ON/OFF
        self._var_enabled = tk.BooleanVar(value=self._enabled)
        def _on_enabled(*_):
            new_state = bool(self._var_enabled.get())
            if new_state != self._enabled:
                self._enabled = new_state
                self._save_state()
                if self._enabled:
                    self._start_server()
                else:
                    self._stop_server()
                self._update_ui()
        self._var_enabled.trace_add("write", _on_enabled)
        ttk.Checkbutton(main_f, text=_t("chk_enabled"), variable=self._var_enabled).pack(anchor="w", pady=(0, 8))

        # ── ネットワーク設定 ──
        lf_net = ttk.LabelFrame(main_f, text=_t("lf_network"), padding=8)
        lf_net.pack(fill=tk.X, pady=(0, 8))

        # 受信ポート
        row1 = ttk.Frame(lf_net)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text=_t("label_recv_port"), width=24).pack(side="left")
        self._var_recv_port = tk.IntVar(value=self._recv_port)
        ent_port = ttk.Entry(row1, textvariable=self._var_recv_port, width=10)
        ent_port.pack(side="left")

        # 送信先URL
        row2 = ttk.Frame(lf_net)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text=_t("label_send_url"), width=24).pack(side="left")
        self._var_send_url = tk.StringVar(value=self._send_url)
        ent_url = ttk.Entry(row2, textvariable=self._var_send_url)
        ent_url.pack(side="left", fill=tk.X, expand=True)

        # 自分の名前
        row3 = ttk.Frame(lf_net)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text=_t("label_speaker"), width=24).pack(side="left")
        self._var_speaker = tk.StringVar(value=self._speaker_name)
        ent_speaker = ttk.Entry(row3, textvariable=self._var_speaker, width=20)
        ent_speaker.pack(side="left")

        # ── ループ制御 ──
        lf_loop = ttk.LabelFrame(main_f, text=_t("lf_loop_control"), padding=8)
        lf_loop.pack(fill=tk.X, pady=(0, 8))

        row4 = ttk.Frame(lf_loop)
        row4.pack(fill=tk.X, pady=2)
        ttk.Label(row4, text=_t("label_min_interval"), width=24).pack(side="left")
        self._var_min_interval = tk.DoubleVar(value=self._min_interval_sec)
        ttk.Spinbox(row4, from_=0.0, to=60.0, increment=1.0, textvariable=self._var_min_interval, width=8).pack(side="left")

        row5 = ttk.Frame(lf_loop)
        row5.pack(fill=tk.X, pady=2)
        ttk.Label(row5, text=_t("label_max_turns"), width=24).pack(side="left")
        self._var_max_turns = tk.IntVar(value=self._max_turns)
        ttk.Spinbox(row5, from_=0, to=999, increment=1, textvariable=self._var_max_turns, width=8).pack(side="left")

        # ── 状態表示 ──
        lf_status = ttk.LabelFrame(main_f, text=_t("lf_status"), padding=8)
        lf_status.pack(fill=tk.X, pady=(0, 8))

        self._lbl_server_var = tk.StringVar(value=f"{_t('label_server')} -")
        ttk.Label(lf_status, textvariable=self._lbl_server_var, font=("", 10, "bold")).pack(anchor="w", pady=2)

        self._lbl_sent_var = tk.StringVar(value=f"{_t('label_sent')} 0")
        ttk.Label(lf_status, textvariable=self._lbl_sent_var).pack(anchor="w")

        self._lbl_recv_var = tk.StringVar(value=f"{_t('label_recv')} 0")
        ttk.Label(lf_status, textvariable=self._lbl_recv_var).pack(anchor="w")

        self._lbl_turn_var = tk.StringVar(value=f"{_t('label_turn')} 0")
        ttk.Label(lf_status, textvariable=self._lbl_turn_var).pack(anchor="w")

        # ── ボタン ──
        btn_f = ttk.Frame(main_f)
        btn_f.pack(fill=tk.X, pady=(0, 8))

        self._btn_pause = tk.Button(
            btn_f,
            text=_t("btn_pause") if not self._paused else _t("btn_resume"),
            bg="#f0ad4e", fg="white", font=("", 10, "bold"),
            command=self._toggle_pause
        )
        self._btn_pause.pack(side="left", fill=tk.X, expand=True, padx=(0, 4))

        tk.Button(
            btn_f, text=_t("btn_reset_turn"),
            bg="#5bc0de", fg="white", font=("", 10),
            command=self._reset_turn
        ).pack(side="left", fill=tk.X, expand=True)

        # 閉じるボタン
        tk.Button(
            main_f, text=_t("btn_close"),
            bg="#6c757d", fg="white", font=("", 10, "bold"),
            command=self._save_and_close
        ).pack(fill=tk.X)

        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)
        self._update_ui()

    def _toggle_pause(self):
        self._paused = not self._paused
        self._update_ui()
        logger.info(f"[TeloponBridge] {'⏸ 一時停止' if self._paused else '▶ 再開'}")

    def _reset_turn(self):
        self._turn_count = 0
        self._update_ui()
        logger.info("[TeloponBridge] 🔄 ターンカウンタをリセット")

    def _update_ui(self):
        if not self._panel or not self._panel.winfo_exists():
            return
        try:
            # サーバー状態
            if self._enabled and self._server is not None:
                if self._paused:
                    text = _t("status_paused")
                else:
                    text = _t("status_running") + f" :{self._recv_port}"
            else:
                text = _t("status_stopped")
            self._lbl_server_var.set(f"{_t('label_server')} {text}")

            # カウンタ
            self._lbl_sent_var.set(f"{_t('label_sent')} {self._sent_count}")
            self._lbl_recv_var.set(f"{_t('label_recv')} {self._recv_count}")
            self._lbl_turn_var.set(f"{_t('label_turn')} {self._turn_count}")

            # 一時停止ボタンのテキスト
            if self._btn_pause:
                self._btn_pause.config(
                    text=_t("btn_resume") if self._paused else _t("btn_pause"),
                    bg="#5cb85c" if self._paused else "#f0ad4e"
                )
        except Exception:
            pass

    def _update_ui_safe(self):
        """別スレッドからUIを更新する（after経由でメインスレッドへ）"""
        if self._panel and self._panel.winfo_exists():
            try:
                self._panel.after(0, self._update_ui)
            except Exception:
                pass

    def _save_and_close(self):
        # フォームから値を回収
        try:
            self._recv_port = int(self._var_recv_port.get())
            self._send_url = str(self._var_send_url.get()).strip()
            self._speaker_name = str(self._var_speaker.get()).strip() or "AI"
            self._min_interval_sec = float(self._var_min_interval.get())
            self._max_turns = int(self._var_max_turns.get())
        except (ValueError, tk.TclError):
            logger.warning("[TeloponBridge] 入力値が不正なため保存をスキップ")

        self._save_state()

        # ポート変更時はサーバーを再起動
        if self._enabled:
            self._stop_server()
            self._start_server()

        self._panel.destroy()
        self._panel = None

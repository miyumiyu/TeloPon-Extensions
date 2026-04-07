"""
TelopTTS - テロップ読み上げプラグイン

AIが出力したテロップの MAIN テキストを Gemini TTS API で音声に変換し再生します。
TeloPon と同じ API キーを使用します。
badge（感情タグ）をTTSプロンプトに自動付加して感情込みの読み上げが可能です。
"""
import re
import threading
import tkinter as tk
from tkinter import ttk
from collections import deque
from plugin_manager import BasePlugin

import config
import logger

try:
    import pyaudio
except ImportError:
    pyaudio = None

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "テロップ読み上げ",
        "panel_title": "🔊 テロップ読み上げ設定",
        "label_voice": "🎙️ 音声:",
        "label_speed": "⏩ スピード:",
        "label_volume": "🔊 音量:",
        "label_delay": "⏳ ディレイ（秒）:",
        "label_read_topic": "📌 TOPICも読み上げる",
        "label_status": "状態:",
        "status_ready": "待機中",
        "status_speaking": "🔊 読み上げ中...",
        "status_error": "⚠️ エラー",
        "status_no_key": "⚠️ APIキー未設定",
        "btn_test": "▶ テスト再生",
        "btn_close": "閉じる",
        "test_text": "テロップ読み上げのテストです。",
        "speed_slow": "ゆっくり",
        "speed_normal": "普通",
        "speed_fast": "早口",
    },
    "en": {
        "plugin_name": "Telop TTS",
        "panel_title": "🔊 Telop TTS Settings",
        "label_voice": "🎙️ Voice:",
        "label_speed": "⏩ Speed:",
        "label_volume": "🔊 Volume:",
        "label_delay": "⏳ Delay (sec):",
        "label_read_topic": "📌 Read TOPIC aloud",
        "label_status": "Status:",
        "status_ready": "Ready",
        "status_speaking": "🔊 Speaking...",
        "status_error": "⚠️ Error",
        "status_no_key": "⚠️ No API Key",
        "btn_test": "▶ Test",
        "btn_close": "Close",
        "test_text": "This is a TTS test for telop readout.",
        "speed_slow": "Slow",
        "speed_normal": "Normal",
        "speed_fast": "Fast",
    },
    "ko": {
        "plugin_name": "텔롭 읽기",
        "panel_title": "🔊 텔롭 읽기 설정",
        "label_voice": "🎙️ 음성:",
        "label_speed": "⏩ 속도:",
        "label_volume": "🔊 볼륨:",
        "label_delay": "⏳ 딜레이 (초):",
        "label_read_topic": "📌 TOPIC도 읽기",
        "label_status": "상태:",
        "status_ready": "대기 중",
        "status_speaking": "🔊 읽는 중...",
        "status_error": "⚠️ 오류",
        "status_no_key": "⚠️ API 키 없음",
        "btn_test": "▶ 테스트",
        "btn_close": "닫기",
        "test_text": "텔롭 읽기 테스트입니다.",
        "speed_slow": "느리게",
        "speed_normal": "보통",
        "speed_fast": "빠르게",
    },
    "ru": {
        "plugin_name": "Озвучка телопов",
        "panel_title": "🔊 Настройки озвучки",
        "label_voice": "🎙️ Голос:",
        "label_speed": "⏩ Скорость:",
        "label_volume": "🔊 Громкость:",
        "label_delay": "⏳ Задержка (сек):",
        "label_read_topic": "📌 Читать TOPIC",
        "label_status": "Статус:",
        "status_ready": "Готов",
        "status_speaking": "🔊 Озвучка...",
        "status_error": "⚠️ Ошибка",
        "status_no_key": "⚠️ Нет API ключа",
        "btn_test": "▶ Тест",
        "btn_close": "Закрыть",
        "test_text": "Это тест озвучки телопов.",
        "speed_slow": "Медленно",
        "speed_normal": "Обычно",
        "speed_fast": "Быстро",
    },
}

VOICES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
    "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
    "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat",
]

# スピード → TTS プロンプト指示
_SPEED_PROMPTS = {
    "slow":   "ゆっくり落ち着いたペースで読んでください: ",
    "normal": "",
    "fast":   "テンポよく早口で読んでください: ",
}

TTS_MODEL = "gemini-2.5-flash-preview-tts"
TTS_SAMPLE_RATE = 24000
TTS_CHANNELS = 1
TTS_SAMPLE_WIDTH = 2  # 16-bit


def _t(key):
    import i18n
    lang = getattr(i18n, '_current_language', 'en') or 'en'
    lang = lang[:2]
    return _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))


def _strip_tags(text):
    """HTMLタグ・テロップタグを除去してプレーンテキストにする"""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[/?b[12]\]', '', text)
    return text.strip()


class TelopTTSPlugin(BasePlugin):
    PLUGIN_ID   = "telop_tts"
    PLUGIN_NAME = "Telop TTS"
    PLUGIN_TYPE = "TOOL"

    def __init__(self):
        super().__init__()
        self._panel = None
        self._status_label = None
        self._tts_queue = deque(maxlen=10)
        self._worker_thread = None
        self._worker_running = False
        self._volume = 100
        self._voice = "Kore"
        self._speed = "normal"
        self._delay = 0
        self._read_topic = False
        self._enabled = False
        self.is_running = False  # バッジ表示用（ON/OFF連動）

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {"enabled": False, "voice": "Kore", "volume": 100,
                "speed": "normal", "delay": 0, "read_topic": False}

    def start(self, prompt_config, message_queue):
        self._load_settings()
        self._start_worker()

    def stop(self):
        self._stop_worker()

    def _load_settings(self):
        settings = self.get_settings()
        self._voice = settings.get("voice", "Kore")
        self._volume = int(settings.get("volume", 100))
        self._speed = settings.get("speed", "normal")
        self._delay = int(settings.get("delay", 0))
        self._read_topic = settings.get("read_topic", False)
        self._enabled = settings.get("enabled", False)
        self.is_running = self._enabled
        # ディレイは起動時0。UIで変更された時に set_telop_delay が呼ばれる

    def _start_worker(self):
        if self._worker_running:
            return
        self._worker_running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def _stop_worker(self):
        self._worker_running = False
        self._tts_queue.clear()

    # --------------------------------------------------------
    # テロップ出力フック
    # --------------------------------------------------------
    def on_telop_output(self, topic, main, window, layout, badge):
        if not self._enabled or not main:
            return
        clean_main = _strip_tags(main)
        if not clean_main:
            return

        # 読み上げテキスト構築
        if self._read_topic and topic:
            clean_topic = _strip_tags(topic)
            read_text = f"{clean_topic}。{clean_main}" if clean_topic else clean_main
        else:
            read_text = clean_main

        # badge（感情）+ スピード指示をプロンプトに付加
        prompt_prefix = ""
        speed_prefix = _SPEED_PROMPTS.get(self._speed, "")
        if badge and badge != "NONE":
            prompt_prefix = f"{badge}な感じで"
            if speed_prefix:
                prompt_prefix += "、" + speed_prefix.rstrip(": ")
            prompt_prefix += "読んでください: "
        elif speed_prefix:
            prompt_prefix = speed_prefix

        tts_text = prompt_prefix + read_text
        self._tts_queue.append(tts_text)
        if not self._worker_running:
            self._start_worker()

    # --------------------------------------------------------
    # TTS ワーカー（別スレッド）
    # --------------------------------------------------------
    def _worker_loop(self):
        import time
        while self._worker_running:
            if not self._tts_queue:
                time.sleep(0.1)
                continue
            text = self._tts_queue.popleft()
            self._set_status(_t("status_speaking"))
            try:
                self._speak(text)
            except Exception as e:
                logger.warning(f"[TelopTTS] 読み上げエラー: {e}")
                self._set_status(_t("status_error"))
                time.sleep(1)
                continue
            self._set_status(_t("status_ready"))

    def _speak(self, text):
        """Gemini TTS API でテキストを音声に変換して再生する"""
        from google import genai
        from google.genai import types

        api_key = config.app_config.get("api_key", "")
        if not api_key:
            logger.warning("[TelopTTS] APIキーが設定されていません")
            self._set_status(_t("status_no_key"))
            return

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=TTS_MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self._voice,
                        )
                    )
                ),
            )
        )

        pcm_data = response.candidates[0].content.parts[0].inline_data.data
        if not pcm_data:
            return

        # 音量調整
        if self._volume < 100:
            import struct
            factor = self._volume / 100.0
            samples = struct.unpack(f"<{len(pcm_data)//2}h", pcm_data)
            adjusted = struct.pack(f"<{len(samples)}h",
                                   *[max(-32768, min(32767, int(s * factor))) for s in samples])
            pcm_data = adjusted

        # pyaudio で再生
        if not pyaudio:
            logger.warning("[TelopTTS] pyaudio が利用できません")
            return

        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=TTS_CHANNELS,
                rate=TTS_SAMPLE_RATE,
                output=True,
            )
            chunk_size = TTS_SAMPLE_RATE * TTS_SAMPLE_WIDTH  # 1秒分
            offset = 0
            while offset < len(pcm_data) and self._worker_running:
                end = min(offset + chunk_size, len(pcm_data))
                stream.write(pcm_data[offset:end])
                offset = end
            stream.stop_stream()
            stream.close()
        finally:
            p.terminate()

        logger.debug(f"[TelopTTS] 再生完了: {text[:50]}...")

    def _set_status(self, text):
        """ステータスラベル更新（メインスレッドに委譲）"""
        if self._panel and self._status_label:
            try:
                self._panel.after(0, lambda: self._status_label.config(text=text))
            except Exception:
                pass

    # --------------------------------------------------------
    # 操作パネル UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._load_settings()

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("panel_title"))
        self._panel.geometry("420x340")
        self._panel.minsize(380, 320)

        main_f = ttk.Frame(self._panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # ON/OFF
        self._enabled_var = tk.BooleanVar(value=self._enabled)
        ttk.Checkbutton(main_f, text="ON / OFF", variable=self._enabled_var,
                         command=self._on_toggle).pack(anchor="w", pady=(0, 5))

        # TOPIC読み上げ ON/OFF
        self._topic_var = tk.BooleanVar(value=self._read_topic)
        ttk.Checkbutton(main_f, text=_t("label_read_topic"), variable=self._topic_var,
                         command=self._on_topic_changed).pack(anchor="w", pady=(0, 8))

        # 音声選択
        row_voice = ttk.Frame(main_f)
        row_voice.pack(fill=tk.X, pady=3)
        ttk.Label(row_voice, text=_t("label_voice")).pack(side=tk.LEFT)
        self._voice_var = tk.StringVar(value=self._voice)
        combo_voice = ttk.Combobox(row_voice, textvariable=self._voice_var,
                                    values=VOICES, state="readonly", width=18)
        combo_voice.pack(side=tk.LEFT, padx=(5, 0))
        combo_voice.bind("<<ComboboxSelected>>", self._on_voice_changed)

        # スピード
        row_speed = ttk.Frame(main_f)
        row_speed.pack(fill=tk.X, pady=3)
        ttk.Label(row_speed, text=_t("label_speed")).pack(side=tk.LEFT)
        speed_items = [_t("speed_slow"), _t("speed_normal"), _t("speed_fast")]
        self._speed_var = tk.StringVar()
        speed_map = {"slow": speed_items[0], "normal": speed_items[1], "fast": speed_items[2]}
        self._speed_var.set(speed_map.get(self._speed, speed_items[1]))
        combo_speed = ttk.Combobox(row_speed, textvariable=self._speed_var,
                                    values=speed_items, state="readonly", width=10)
        combo_speed.pack(side=tk.LEFT, padx=(5, 0))
        combo_speed.bind("<<ComboboxSelected>>", self._on_speed_changed)
        self._speed_reverse_map = {v: k for k, v in speed_map.items()}

        # 音量
        row_vol = ttk.Frame(main_f)
        row_vol.pack(fill=tk.X, pady=3)
        ttk.Label(row_vol, text=_t("label_volume")).pack(side=tk.LEFT)
        self._vol_var = tk.IntVar(value=self._volume)
        self._vol_label = ttk.Label(row_vol, text=f"{self._volume}%", width=5)
        self._vol_label.pack(side=tk.RIGHT)
        ttk.Scale(row_vol, from_=0, to=100, variable=self._vol_var,
                  command=self._on_volume_changed).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        # ディレイ
        row_delay = ttk.Frame(main_f)
        row_delay.pack(fill=tk.X, pady=3)
        ttk.Label(row_delay, text=_t("label_delay")).pack(side=tk.LEFT)
        self._delay_var = tk.IntVar(value=self._delay)
        self._delay_label = ttk.Label(row_delay, text=f"{self._delay}s", width=5)
        self._delay_label.pack(side=tk.RIGHT)
        ttk.Scale(row_delay, from_=0, to=10, variable=self._delay_var,
                  command=self._on_delay_changed).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        # テスト再生
        ttk.Button(main_f, text=_t("btn_test"), command=self._test_play).pack(fill=tk.X, pady=(8, 4))

        # ステータス
        row_status = ttk.Frame(main_f)
        row_status.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row_status, text=_t("label_status")).pack(side=tk.LEFT)
        self._status_label = ttk.Label(row_status, text=_t("status_ready"))
        self._status_label.pack(side=tk.LEFT, padx=(5, 0))

        # 閉じるボタン
        tk.Button(main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
                  font=("", 10, "bold"), command=self._close_panel).pack(fill=tk.X, pady=(10, 0))
        self._panel.protocol("WM_DELETE_WINDOW", self._close_panel)

    # --------------------------------------------------------
    # UIイベントハンドラ
    # --------------------------------------------------------
    def _close_panel(self):
        self._save_current()
        self._panel.destroy()

    def _on_toggle(self):
        self._enabled = self._enabled_var.get()
        self.is_running = self._enabled  # バッジ表示を連動
        self._save_current()
        if self._enabled and not self._worker_running:
            self._start_worker()

    def _on_topic_changed(self):
        self._read_topic = self._topic_var.get()
        self._save_current()

    def _on_voice_changed(self, event=None):
        self._voice = self._voice_var.get()
        self._save_current()

    def _on_speed_changed(self, event=None):
        display = self._speed_var.get()
        self._speed = self._speed_reverse_map.get(display, "normal")
        self._save_current()

    def _on_volume_changed(self, value=None):
        self._volume = int(self._vol_var.get())
        self._vol_label.config(text=f"{self._volume}%")
        self._save_current()

    def _on_delay_changed(self, value=None):
        self._delay = int(self._delay_var.get())
        self._delay_label.config(text=f"{self._delay}s")
        self.set_telop_delay(self._delay)
        self._save_current()

    def _save_current(self):
        settings = self.get_settings()
        settings["enabled"] = self._enabled
        settings["voice"] = self._voice
        settings["volume"] = self._volume
        settings["speed"] = self._speed
        settings["delay"] = self._delay
        settings["read_topic"] = self._read_topic
        self.save_settings(settings)

    def _test_play(self):
        text = _t("test_text")
        self._tts_queue.append(text)
        if not self._worker_running:
            self._start_worker()

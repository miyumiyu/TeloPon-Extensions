"""
VoicevoxPlugin v1.00 - VOICEVOX テロップ読み上げプラグイン

AIが出力したテロップの MAIN テキストを VOICEVOX の HTTP API で読み上げます。

必要環境:
  - VOICEVOX GUI アプリが起動済みであること（デフォルト: localhost:50021）
  - requests ライブラリ（TeloPon 同梱）
  - pyaudio ライブラリ（TeloPon 同梱）
"""

import base64
import io
import queue
import re
import threading
import wave
import tkinter as tk
from tkinter import ttk

import logger
from plugin_manager import BasePlugin

try:
    import requests
except ImportError:
    requests = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "VOICEVOX読み上げ",
        "window_title": "⚙️ VOICEVOX設定",
        "lf_conn": " VOICEVOX接続設定 ",
        "label_url": "URL:",
        "btn_test": "接続テスト",
        "lf_voice": " 音声設定 ",
        "label_character": "キャラクター:",
        "label_style": "性格（スタイル）:",
        "label_speed": "話速:",
        "label_volume": "音量:",
        "label_pitch": "音高:",
        "label_intonation": "抑揚:",
        "label_pre_phoneme": "発話前無音:",
        "lf_telop": " テロップ設定 ",
        "label_show_telop": "📺 テロップを表示する",
        "label_delay": "テロップのディレイ（秒）:",
        "label_read_topic": "📌 TOPICも読み上げる",
        "btn_close": "閉じる",
        "btn_refresh": "🔄",
        "test_ok": "✅ 接続成功",
        "test_fail": "❌ 接続失敗: VOICEVOXが起動しているか確認してください",
        "warn_no_requests": "requestsライブラリが見つかりません",
        "warn_no_pyaudio": "pyaudioライブラリが見つかりません",
        "no_speakers": "（VOICEVOXに接続して取得）",
    },
    "en": {
        "plugin_name": "VOICEVOX TTS",
        "window_title": "⚙️ VOICEVOX Settings",
        "lf_conn": " VOICEVOX Connection ",
        "label_url": "URL:",
        "btn_test": "Test Connection",
        "lf_voice": " Voice Settings ",
        "label_character": "Character:",
        "label_style": "Style:",
        "label_speed": "Speed:",
        "label_volume": "Volume:",
        "label_pitch": "Pitch:",
        "label_intonation": "Intonation:",
        "label_pre_phoneme": "Pre-silence:",
        "lf_telop": " Telop Settings ",
        "label_show_telop": "📺 Show Telop",
        "label_delay": "Telop Delay (sec):",
        "label_read_topic": "📌 Read TOPIC aloud",
        "btn_close": "Close",
        "btn_refresh": "🔄",
        "test_ok": "✅ Connection successful",
        "test_fail": "❌ Connection failed: Make sure VOICEVOX is running",
        "warn_no_requests": "requests library not found",
        "warn_no_pyaudio": "pyaudio library not found",
        "no_speakers": "(Connect to VOICEVOX to load)",
    },
    "ko": {
        "plugin_name": "VOICEVOX 읽기",
        "window_title": "⚙️ VOICEVOX 설정",
        "lf_conn": " VOICEVOX 연결 설정 ",
        "label_url": "URL:",
        "btn_test": "연결 테스트",
        "lf_voice": " 음성 설정 ",
        "label_character": "캐릭터:",
        "label_style": "스타일:",
        "label_speed": "속도:",
        "label_volume": "음량:",
        "label_pitch": "음높이:",
        "label_intonation": "억양:",
        "label_pre_phoneme": "발화 전 무음:",
        "lf_telop": " 텔롭 설정 ",
        "label_show_telop": "📺 텔롭 표시",
        "label_delay": "텔롭 딜레이 (초):",
        "label_read_topic": "📌 TOPIC도 읽기",
        "btn_close": "닫기",
        "btn_refresh": "🔄",
        "test_ok": "✅ 연결 성공",
        "test_fail": "❌ 연결 실패: VOICEVOX가 실행 중인지 확인하세요",
        "warn_no_requests": "requests 라이브러리를 찾을 수 없습니다",
        "warn_no_pyaudio": "pyaudio 라이브러리를 찾을 수 없습니다",
        "no_speakers": "(VOICEVOX에 연결하여 로드)",
    },
    "ru": {
        "plugin_name": "VOICEVOX TTS",
        "window_title": "⚙️ Настройки VOICEVOX",
        "lf_conn": " Подключение VOICEVOX ",
        "label_url": "URL:",
        "btn_test": "Тест подключения",
        "lf_voice": " Настройки голоса ",
        "label_character": "Персонаж:",
        "label_style": "Стиль:",
        "label_speed": "Скорость:",
        "label_volume": "Громкость:",
        "label_pitch": "Высота тона:",
        "label_intonation": "Интонация:",
        "label_pre_phoneme": "Тишина перед речью:",
        "lf_telop": " Настройки телопа ",
        "label_show_telop": "📺 Показать телоп",
        "label_delay": "Задержка телопа (сек):",
        "label_read_topic": "📌 Читать TOPIC",
        "btn_close": "Закрыть",
        "btn_refresh": "🔄",
        "test_ok": "✅ Подключение успешно",
        "test_fail": "❌ Ошибка подключения: убедитесь, что VOICEVOX запущен",
        "warn_no_requests": "Библиотека requests не найдена",
        "warn_no_pyaudio": "Библиотека pyaudio не найдена",
        "no_speakers": "(Подключитесь к VOICEVOX для загрузки)",
    },
}

def _t(key):
    try:
        import i18n
        lang = getattr(i18n, '_current_language', 'ja') or 'ja'
        lang = lang[:2]
    except Exception:
        lang = "ja"
    return _L.get(lang, _L["ja"]).get(key, _L["ja"].get(key, key))


def _strip_markup(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\[/?b[12]\]', '', text)
    text = re.sub(r'</?b[012]>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


class VoicevoxPlugin(BasePlugin):
    PLUGIN_ID   = "voicevox"
    PLUGIN_NAME = "VOICEVOX読み上げ"
    PLUGIN_TYPE = "TOOL"

    def get_display_name(self):
        return _t("plugin_name")

    def __init__(self):
        super().__init__()
        self._speech_queue = queue.Queue(maxsize=1)
        self._stop_event = threading.Event()
        self._panel = None

        # スピーカーキャッシュ: [{name, speaker_uuid, styles: [{name, id}]}]
        self._speakers = []
        self._icon_image = None  # Tkinter PhotoImage 保持用

        # 設定のライブキャッシュ
        saved = self.get_settings()
        self._live_enabled    = saved.get("enabled", False)
        self._live_delay      = int(saved.get("telop_delay", 0))
        self._live_speed      = float(saved.get("speed_scale", 1.0))
        self._live_volume     = float(saved.get("volume_scale", 1.0))
        self._live_pitch      = float(saved.get("pitch_scale", 0.0))
        self._live_intonation = float(saved.get("intonation_scale", 1.0))
        self._live_pre_phoneme = float(saved.get("pre_phoneme_length", 0.1))
        self._live_speaker_id = int(saved.get("speaker_id", 3))
        self._live_read_topic = saved.get("read_topic", False)
        self._live_show_telop = saved.get("show_telop", True)
        self._connected = False  # VOICEVOX接続状態

        if requests is None:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('warn_no_requests')}")
        elif pyaudio is None:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('warn_no_pyaudio')}")
        else:
            # 起動時に接続確認
            if self._live_enabled:
                url = saved.get("url", "http://localhost:50021").rstrip("/")
                if self._check_connection(url):
                    self._connected = True
                    self._fetch_speakers(url)
                    logger.info(f"[{self.PLUGIN_NAME}] 起動時にVOICEVOXへの接続を確認しました")
                else:
                    self._live_enabled = False
                    logger.warning(f"[{self.PLUGIN_NAME}] VOICEVOXに接続できません。読み上げをOFFにしました")
            # ワーカースレッド起動
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()

        self.is_running = self._live_enabled
        # ディレイは起動時0。UIで変更された時に _update_telop_delay が呼ばれる

    def get_default_settings(self):
        return {
            "enabled": False,
            "url": "http://localhost:50021",
            "speaker_id": 3,
            "speaker_name": "",
            "style_name": "",
            "speed_scale": 1.0,
            "volume_scale": 1.0,
            "pitch_scale": 0.0,
            "intonation_scale": 1.0,
            "pre_phoneme_length": 0.1,
            "telop_delay": 0,
            "show_telop": True,
            "read_topic": False,
        }

    def _update_telop_delay(self):
        """enabled / show_telop / delay 値からディレイを更新する"""
        if not self._live_enabled:
            self.set_telop_delay(0)
        elif self._live_show_telop:
            self.set_telop_delay(self._live_delay)
        else:
            self.set_telop_delay(-1)

    def start(self, prompt_config, message_queue):
        pass

    def stop(self):
        pass

    # --------------------------------------------------------
    # テロップ出力フック
    # --------------------------------------------------------
    def on_telop_output(self, topic, main, window, layout, badge):
        if not self._live_enabled:
            return

        # 初めて反応したタイミングでディレイを有効化（起動時は0のまま）
        self._update_telop_delay()

        clean_main = _strip_markup(main)
        if not clean_main:
            return

        if self._live_read_topic and topic:
            clean_topic = _strip_markup(topic)
            text = f"{clean_topic}。{clean_main}" if clean_topic else clean_main
        else:
            text = clean_main

        try:
            self._speech_queue.get_nowait()
        except queue.Empty:
            pass
        try:
            self._speech_queue.put_nowait(text)
        except queue.Full:
            pass

    # --------------------------------------------------------
    # 音声合成ワーカー
    # --------------------------------------------------------
    def _worker_loop(self):
        while not self._stop_event.is_set():
            try:
                text = self._speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if text is None:
                break
            try:
                self._synthesize_and_play(text)
            except (requests.ConnectionError, requests.Timeout, ConnectionRefusedError, OSError) as e:
                logger.warning(f"[{self.PLUGIN_NAME}] VOICEVOX接続エラー。読み上げをOFFにします: {e}")
                self._live_enabled = False
                self._connected = False
                self.is_running = False
                # パネルが開いていたらUIも連動
                if self._panel and self._panel.winfo_exists():
                    try:
                        self._panel.after(0, lambda: (
                            self._var_enabled.set(False),
                            self._set_voice_ui_state(False),
                            self._lbl_test.config(text=_t("test_fail"), foreground="red"),
                        ))
                    except Exception:
                        pass
                break
            except Exception as e:
                logger.warning(f"[{self.PLUGIN_NAME}] 読み上げエラー: {e}")

    def _synthesize_and_play(self, text: str):
        settings = self.get_settings()
        base_url   = settings.get("url", "http://localhost:50021").rstrip("/")
        speaker_id = self._live_speaker_id
        speed      = self._live_speed
        volume     = self._live_volume

        query_resp = requests.post(
            f"{base_url}/audio_query",
            params={"text": text, "speaker": speaker_id},
            timeout=10,
        )
        if query_resp.status_code != 200:
            logger.warning(f"[{self.PLUGIN_NAME}] audio_query 失敗: {query_resp.status_code}")
            return

        query_data = query_resp.json()
        query_data["speedScale"]       = speed
        query_data["volumeScale"]      = volume
        query_data["pitchScale"]       = self._live_pitch
        query_data["intonationScale"]  = self._live_intonation
        query_data["prePhonemeLength"] = self._live_pre_phoneme

        if self._stop_event.is_set():
            return

        synth_resp = requests.post(
            f"{base_url}/synthesis",
            json=query_data,
            params={"speaker": speaker_id},
            timeout=15,
        )
        if synth_resp.status_code != 200:
            logger.warning(f"[{self.PLUGIN_NAME}] synthesis 失敗: {synth_resp.status_code}")
            return

        if self._stop_event.is_set():
            return

        self._play_wav(synth_resp.content)

    def _play_wav(self, wav_bytes: bytes):
        p = pyaudio.PyAudio()
        try:
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                stream = p.open(
                    format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                )
                try:
                    chunk = 1024
                    data = wf.readframes(chunk)
                    while data and not self._stop_event.is_set():
                        stream.write(data)
                        data = wf.readframes(chunk)
                finally:
                    stream.stop_stream()
                    stream.close()
        finally:
            p.terminate()

    # --------------------------------------------------------
    # VOICEVOX 接続・スピーカー取得
    # --------------------------------------------------------
    def _check_connection(self, base_url):
        """VOICEVOX への接続を確認する"""
        try:
            resp = requests.get(f"{base_url}/version", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def _fetch_speakers(self, base_url):
        """VOICEVOX /speakers API からキャラクター一覧を取得"""
        try:
            resp = requests.get(f"{base_url}/speakers", timeout=5)
            if resp.status_code == 200:
                self._speakers = resp.json()
                logger.info(f"[{self.PLUGIN_NAME}] スピーカー {len(self._speakers)} 件取得")
                return True
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] スピーカー取得失敗: {e}")
        self._speakers = []
        return False

    def _fetch_icon(self, base_url, speaker_uuid, style_id=None):
        """VOICEVOX /speaker_info API からアイコン画像を取得。
        style_id 指定時はそのスタイルのアイコンを返す。"""
        if not Image or not ImageTk:
            return None
        try:
            resp = requests.get(f"{base_url}/speaker_info",
                                params={"speaker_uuid": speaker_uuid, "resource_format": "base64"},
                                timeout=5)
            if resp.status_code == 200:
                info = resp.json()
                style_infos = info.get("style_infos", [])
                # style_id に一致する style_info を探す
                icon_b64 = ""
                if style_id is not None:
                    for si in style_infos:
                        if si.get("id") == style_id:
                            icon_b64 = si.get("icon", "")
                            break
                # 見つからなければ最初のスタイルのアイコン
                if not icon_b64 and style_infos:
                    icon_b64 = style_infos[0].get("icon", "")
                if icon_b64:
                    icon_bytes = base64.b64decode(icon_b64)
                    img = Image.open(io.BytesIO(icon_bytes))
                    img = img.resize((80, 80), Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.debug(f"[{self.PLUGIN_NAME}] アイコン取得失敗: {e}")
        return None

    # --------------------------------------------------------
    # 設定 UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("window_title"))
        self._panel.geometry("420x680")
        self._panel.resizable(False, True)
        self._panel.attributes("-topmost", True)

        settings = self.get_settings()
        main_f = ttk.Frame(self._panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # --- 読み上げ ON/OFF ---
        self._var_enabled = tk.BooleanVar(value=self._live_enabled)
        def _on_enabled_change(*_):
            self._live_enabled = self._var_enabled.get()
            self.is_running = self._live_enabled
            self._update_telop_delay()  # 無効化時は delay を 0 にリセット
        self._var_enabled.trace_add("write", _on_enabled_change)
        self._chk_enabled = ttk.Checkbutton(main_f, text="読み上げ ON", variable=self._var_enabled)
        self._chk_enabled.pack(anchor="w", pady=(0, 5))

        # --- TOPIC読み上げ ---
        self._var_read_topic = tk.BooleanVar(value=self._live_read_topic)
        def _on_topic_change(*_):
            self._live_read_topic = self._var_read_topic.get()
        self._var_read_topic.trace_add("write", _on_topic_change)
        self._chk_topic = ttk.Checkbutton(main_f, text=_t("label_read_topic"), variable=self._var_read_topic)
        self._chk_topic.pack(anchor="w", pady=(0, 8))

        # --- 接続設定 ---
        lf_conn = ttk.LabelFrame(main_f, text=_t("lf_conn"), padding=10)
        lf_conn.pack(fill=tk.X, pady=(0, 10))

        row_url = ttk.Frame(lf_conn)
        row_url.pack(fill=tk.X)
        ttk.Label(row_url, text=_t("label_url")).pack(side=tk.LEFT, padx=(0, 8))
        self._ent_url = ttk.Entry(row_url, width=22)
        self._ent_url.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._ent_url.insert(0, settings.get("url", "http://localhost:50021"))

        self._lbl_test = ttk.Label(lf_conn, text="")
        self._lbl_test.pack(anchor="w", pady=(6, 0))

        tk.Button(lf_conn, text=_t("btn_test"), bg="#17a2b8", fg="white",
                  command=self._test_and_load).pack(fill=tk.X, pady=(6, 0))

        # --- 音声設定 ---
        self._lf_voice = ttk.LabelFrame(main_f, text=_t("lf_voice"), padding=10)
        self._lf_voice.pack(fill=tk.X, pady=(0, 10))
        lf_voice = self._lf_voice

        # アイコン + キャラクター選択
        row_char = ttk.Frame(lf_voice)
        row_char.pack(fill=tk.X, pady=3)

        self._icon_label = ttk.Label(row_char)
        self._icon_label.pack(side=tk.LEFT, padx=(0, 8))

        char_right = ttk.Frame(row_char)
        char_right.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(char_right, text=_t("label_character")).pack(anchor="w")
        self._char_var = tk.StringVar(value=settings.get("speaker_name", ""))
        self._combo_char = ttk.Combobox(char_right, textvariable=self._char_var,
                                         state="readonly", width=20)
        self._combo_char.pack(fill=tk.X)
        self._combo_char.bind("<<ComboboxSelected>>", self._on_character_changed)

        ttk.Label(char_right, text=_t("label_style")).pack(anchor="w", pady=(4, 0))
        self._style_var = tk.StringVar(value=settings.get("style_name", ""))
        self._combo_style = ttk.Combobox(char_right, textvariable=self._style_var,
                                          state="readonly", width=20)
        self._combo_style.pack(fill=tk.X)
        self._combo_style.bind("<<ComboboxSelected>>", self._on_style_changed)

        # 話速
        row_speed = ttk.Frame(lf_voice)
        row_speed.pack(fill=tk.X, pady=3)
        ttk.Label(row_speed, text=_t("label_speed")).pack(side=tk.LEFT)
        self._speed_var = tk.StringVar(value=f"{self._live_speed:.1f}")
        def _on_speed_change(*_):
            try:
                self._live_speed = max(0.5, min(2.0, float(self._speed_var.get()))
                )
            except (ValueError, TypeError):
                pass
        self._speed_var.trace_add("write", _on_speed_change)
        ttk.Spinbox(lf_voice, from_=0.5, to=2.0, increment=0.1, width=8,
                     format="%.1f", textvariable=self._speed_var).pack(in_=row_speed, side=tk.LEFT, padx=(8, 0))

        # 音量
        row_vol = ttk.Frame(lf_voice)
        row_vol.pack(fill=tk.X, pady=3)
        ttk.Label(row_vol, text=_t("label_volume")).pack(side=tk.LEFT)
        self._volume_var = tk.StringVar(value=f"{self._live_volume:.1f}")
        def _on_volume_change(*_):
            try:
                self._live_volume = max(0.1, min(2.0, float(self._volume_var.get()))
                )
            except (ValueError, TypeError):
                pass
        self._volume_var.trace_add("write", _on_volume_change)
        ttk.Spinbox(lf_voice, from_=0.1, to=2.0, increment=0.1, width=8,
                     format="%.1f", textvariable=self._volume_var).pack(in_=row_vol, side=tk.LEFT, padx=(8, 0))

        # 音高
        row_pitch = ttk.Frame(lf_voice)
        row_pitch.pack(fill=tk.X, pady=3)
        ttk.Label(row_pitch, text=_t("label_pitch")).pack(side=tk.LEFT)
        self._pitch_var = tk.StringVar(value=f"{self._live_pitch:.2f}")
        def _on_pitch_change(*_):
            try:
                self._live_pitch = max(-0.15, min(0.15, float(self._pitch_var.get())))
            except (ValueError, TypeError):
                pass
        self._pitch_var.trace_add("write", _on_pitch_change)
        ttk.Spinbox(lf_voice, from_=-0.15, to=0.15, increment=0.01, width=8,
                     format="%.2f", textvariable=self._pitch_var).pack(in_=row_pitch, side=tk.LEFT, padx=(8, 0))

        # 抑揚
        row_inton = ttk.Frame(lf_voice)
        row_inton.pack(fill=tk.X, pady=3)
        ttk.Label(row_inton, text=_t("label_intonation")).pack(side=tk.LEFT)
        self._intonation_var = tk.StringVar(value=f"{self._live_intonation:.1f}")
        def _on_intonation_change(*_):
            try:
                self._live_intonation = max(0.0, min(2.0, float(self._intonation_var.get())))
            except (ValueError, TypeError):
                pass
        self._intonation_var.trace_add("write", _on_intonation_change)
        ttk.Spinbox(lf_voice, from_=0.0, to=2.0, increment=0.1, width=8,
                     format="%.1f", textvariable=self._intonation_var).pack(in_=row_inton, side=tk.LEFT, padx=(8, 0))

        # 発話前無音
        row_pre = ttk.Frame(lf_voice)
        row_pre.pack(fill=tk.X, pady=3)
        ttk.Label(row_pre, text=_t("label_pre_phoneme")).pack(side=tk.LEFT)
        self._pre_phoneme_var = tk.StringVar(value=f"{self._live_pre_phoneme:.2f}")
        def _on_pre_phoneme_change(*_):
            try:
                self._live_pre_phoneme = max(0.0, min(1.5, float(self._pre_phoneme_var.get())))
            except (ValueError, TypeError):
                pass
        self._pre_phoneme_var.trace_add("write", _on_pre_phoneme_change)
        ttk.Spinbox(lf_voice, from_=0.0, to=1.5, increment=0.05, width=8,
                     format="%.2f", textvariable=self._pre_phoneme_var).pack(in_=row_pre, side=tk.LEFT, padx=(8, 0))

        # --- テロップ設定 ---
        self._lf_telop = ttk.LabelFrame(main_f, text=_t("lf_telop"), padding=10)
        self._lf_telop.pack(fill=tk.X, pady=(0, 10))
        lf_telop = self._lf_telop

        # テロップ表示 ON/OFF
        self._var_show_telop = tk.BooleanVar(value=self._live_show_telop)
        def _on_show_telop_change(*_):
            self._live_show_telop = self._var_show_telop.get()
            self._update_telop_delay()
            # ディレイ Spinbox の有効/無効を切り替え
            state = "normal" if self._live_show_telop else "disabled"
            self._spn_delay.config(state=state)
        self._var_show_telop.trace_add("write", _on_show_telop_change)
        ttk.Checkbutton(lf_telop, text=_t("label_show_telop"),
                         variable=self._var_show_telop).pack(anchor="w", pady=(0, 5))

        row_delay = ttk.Frame(lf_telop)
        row_delay.pack(fill=tk.X)
        ttk.Label(row_delay, text=_t("label_delay")).pack(side=tk.LEFT)
        self._delay_var = tk.StringVar(value=str(self._live_delay))
        def _on_delay_change(*_):
            try:
                self._live_delay = max(0, min(10, int(float(self._delay_var.get()))))
                self._update_telop_delay()
            except (ValueError, TypeError):
                pass
        self._delay_var.trace_add("write", _on_delay_change)
        self._spn_delay = ttk.Spinbox(lf_telop, from_=0, to=10, increment=1, width=8,
                                       textvariable=self._delay_var,
                                       state="normal" if self._live_show_telop else "disabled")
        self._spn_delay.pack(in_=row_delay, side=tk.LEFT, padx=(8, 0))

        # --- 閉じるボタン ---
        tk.Button(main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
                  font=("", 10, "bold"), command=self._save_and_close).pack(fill=tk.X, pady=(10, 0))
        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

        # 接続状態に応じて音声設定の有効/無効を設定
        self._set_voice_ui_state(self._connected)

        # 初回ロード: 保存済みの speaker_name があればスピーカーを取得
        self._try_auto_load(settings)

    def _set_voice_ui_state(self, connected):
        """接続状態に応じて ON/OFF・TOPIC・音声設定・テロップ設定の有効/無効を切り替える"""
        state = "normal" if connected else "disabled"
        # チェックボックス
        self._chk_enabled.config(state=state)
        self._chk_topic.config(state=state)
        # 音声設定内の全子ウィジェット
        for child in self._lf_voice.winfo_children():
            try:
                child.config(state=state)
            except (tk.TclError, AttributeError):
                # Frame 等 state を持たないウィジェットはスキップ
                for sub in child.winfo_children():
                    try:
                        sub.config(state=state)
                    except (tk.TclError, AttributeError):
                        pass
        # テロップ設定内の全子ウィジェット
        for child in self._lf_telop.winfo_children():
            try:
                child.config(state=state)
            except (tk.TclError, AttributeError):
                for sub in child.winfo_children():
                    try:
                        sub.config(state=state)
                    except (tk.TclError, AttributeError):
                        pass

    def _try_auto_load(self, settings):
        """パネル表示時にスピーカー一覧を自動取得してプルダウンを復元"""
        url = self._ent_url.get().strip().rstrip("/")
        if self._check_connection(url) and self._fetch_speakers(url):
            self._connected = True
            self._set_voice_ui_state(True)
            names = [s["name"] for s in self._speakers]
            self._combo_char["values"] = names

            saved_name = settings.get("speaker_name", "")
            if saved_name in names:
                self._char_var.set(saved_name)
                self._update_styles(saved_name)
                saved_style = settings.get("style_name", "")
                if saved_style:
                    self._style_var.set(saved_style)
                self._update_icon(saved_name)
        else:
            self._combo_char["values"] = [_t("no_speakers")]

    def _test_and_load(self):
        """接続テスト + スピーカー一覧取得 + UI状態切り替え"""
        url = self._ent_url.get().strip().rstrip("/")
        try:
            resp = requests.get(f"{url}/version", timeout=3)
            if resp.status_code == 200:
                self._lbl_test.config(text=_t("test_ok"), foreground="green")
                logger.info(f"[{self.PLUGIN_NAME}] VOICEVOX バージョン: {resp.text.strip()}")
                self._connected = True
                self._set_voice_ui_state(True)
                if self._fetch_speakers(url):
                    names = [s["name"] for s in self._speakers]
                    self._combo_char["values"] = names
                    if names:
                        self._char_var.set(names[0])
                        self._on_character_changed()
            else:
                self._lbl_test.config(text=_t("test_fail"), foreground="red")
                self._connected = False
                self._live_enabled = False
                self._var_enabled.set(False)
                self.is_running = False
                self._set_voice_ui_state(False)
        except Exception as e:
            self._lbl_test.config(text=_t("test_fail"), foreground="red")
            self._connected = False
            self._live_enabled = False
            self._var_enabled.set(False)
            self.is_running = False
            self._set_voice_ui_state(False)
            logger.warning(f"[{self.PLUGIN_NAME}] 接続テスト失敗: {e}")

    def _on_character_changed(self, event=None):
        name = self._char_var.get()
        self._update_styles(name)
        self._update_icon(name)

    def _update_styles(self, character_name):
        """選択されたキャラクターのスタイル一覧をプルダウンに設定"""
        for s in self._speakers:
            if s["name"] == character_name:
                styles = s.get("styles", [])
                style_names = [st["name"] for st in styles]
                self._combo_style["values"] = style_names
                if style_names:
                    self._style_var.set(style_names[0])
                    self._on_style_changed()
                return
        self._combo_style["values"] = []

    def _on_style_changed(self, event=None):
        """スタイル選択変更 → speaker_id + アイコンを更新"""
        char_name = self._char_var.get()
        style_name = self._style_var.get()
        for s in self._speakers:
            if s["name"] == char_name:
                for st in s.get("styles", []):
                    if st["name"] == style_name:
                        self._live_speaker_id = st["id"]
                        logger.debug(f"[{self.PLUGIN_NAME}] speaker_id={st['id']} ({char_name} / {style_name})")
                        self._update_icon(char_name, st["id"])
                        return

    def _update_icon(self, character_name, style_id=None):
        """キャラクター（+スタイル）のアイコン画像を取得して表示"""
        url = self._ent_url.get().strip().rstrip("/")
        for s in self._speakers:
            if s["name"] == character_name:
                uuid = s.get("speaker_uuid", "")
                if uuid:
                    icon = self._fetch_icon(url, uuid, style_id)
                    if icon:
                        self._icon_image = icon  # 参照保持（GC防止）
                        self._icon_label.config(image=icon)
                        return
        self._icon_image = None
        self._icon_label.config(image="")

    def _save_and_close(self):
        settings = self.get_settings()
        settings["enabled"]      = self._live_enabled
        settings["telop_delay"]  = self._live_delay
        settings["show_telop"]   = self._live_show_telop
        settings["read_topic"]   = self._live_read_topic
        settings["url"]          = self._ent_url.get().strip().rstrip("/")
        settings["speaker_id"]   = self._live_speaker_id
        settings["speaker_name"] = self._char_var.get() if hasattr(self, '_char_var') else ""
        settings["style_name"]   = self._style_var.get() if hasattr(self, '_style_var') else ""
        settings["speed_scale"]        = self._live_speed
        settings["volume_scale"]       = self._live_volume
        settings["pitch_scale"]        = self._live_pitch
        settings["intonation_scale"]   = self._live_intonation
        settings["pre_phoneme_length"] = self._live_pre_phoneme
        logger.info(f"[{self.PLUGIN_NAME}] 設定を保存: enabled={settings['enabled']}, "
                     f"speaker={settings['speaker_name']}/{settings['style_name']} (id={settings['speaker_id']})")
        self.save_settings(settings)
        self._panel.destroy()

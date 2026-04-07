"""
WindowsTTS v1.00 - Windows標準読み上げプラグイン for TeloPon
=========================================================
pyttsx3 (SAPI5) を使ってテロップのMAINテキストを読み上げる。
pyaudio で再生デバイスを選択可能。

必要ライブラリ: pip install pyttsx3

機能:
  - AIテロップ出力時にMAINテキストを自動読み上げ
  - 音声選択（日本語/英語等、インストール済み音声から選択）
  - 再生デバイス選択
  - 速度・音量調整
  - TOPIC読み上げ ON/OFF
"""

import os
import re
import tempfile
import threading
import time
import tkinter as tk
import wave
from collections import deque
from tkinter import ttk

from plugin_manager import BasePlugin
import logger

_HAS_PYTTSX3 = True
_HAS_PYAUDIO = True
try:
    import pyttsx3
except ImportError:
    _HAS_PYTTSX3 = False

try:
    import pyaudio
except ImportError:
    _HAS_PYAUDIO = False

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "Windows 読み上げ",
        "panel_title": "Windows 読み上げ 設定",
        "chk_enabled": "読み上げ ON",
        "lf_voice": " 音声設定 ",
        "label_voice": "音声:",
        "label_device": "再生デバイス:",
        "label_speed": "速度:",
        "label_pitch": "ピッチ:",
        "pitch_low": "低い",
        "pitch_high": "高い",
        "label_volume": "音量:",
        "speed_slow": "遅い",
        "speed_fast": "速い",
        "vol_low": "小",
        "vol_high": "大",
        "chk_topic": "TOPICも読み上げる",
        "btn_test": "テスト読み上げ",
        "btn_close": "閉じる",
        "test_text": "テスト読み上げです。TeloPonの読み上げプラグインが動作しています。",
        "no_voices": "利用可能な音声が見つかりません",
        "device_default": "既定のデバイス",
        "import_error": "pyttsx3が必要です（pip install pyttsx3）",
    },
    "en": {
        "plugin_name": "Windows TTS",
        "panel_title": "Windows TTS Settings",
        "chk_enabled": "TTS ON",
        "lf_voice": " Voice Settings ",
        "label_voice": "Voice:",
        "label_device": "Output Device:",
        "label_speed": "Speed:",
        "label_pitch": "Pitch:",
        "pitch_low": "Low",
        "pitch_high": "High",
        "label_volume": "Volume:",
        "speed_slow": "Slow",
        "speed_fast": "Fast",
        "vol_low": "Low",
        "vol_high": "High",
        "chk_topic": "Read TOPIC too",
        "btn_test": "Test TTS",
        "btn_close": "Close",
        "test_text": "This is a test. The TeloPon TTS plugin is working.",
        "no_voices": "No voices available",
        "device_default": "Default Device",
        "import_error": "pyttsx3 required (pip install pyttsx3)",
    },
    "ko": {
        "plugin_name": "Windows 음성",
        "panel_title": "Windows 음성 설정",
        "chk_enabled": "음성 ON",
        "lf_voice": " 음성 설정 ",
        "label_voice": "음성:",
        "label_device": "출력 장치:",
        "label_speed": "속도:",
        "label_pitch": "피치:",
        "pitch_low": "낮음",
        "pitch_high": "높음",
        "label_volume": "음량:",
        "speed_slow": "느림",
        "speed_fast": "빠름",
        "vol_low": "작음",
        "vol_high": "큼",
        "chk_topic": "TOPIC도 읽기",
        "btn_test": "테스트",
        "btn_close": "닫기",
        "test_text": "테스트 음성입니다.",
        "no_voices": "사용 가능한 음성이 없습니다",
        "device_default": "기본 장치",
        "import_error": "pyttsx3 필요 (pip install pyttsx3)",
    },
    "ru": {
        "plugin_name": "Windows TTS",
        "panel_title": "Настройки Windows TTS",
        "chk_enabled": "TTS ВКЛ",
        "lf_voice": " Настройки голоса ",
        "label_voice": "Голос:",
        "label_device": "Устройство:",
        "label_speed": "Скорость:",
        "label_pitch": "Тон:",
        "pitch_low": "Низкий",
        "pitch_high": "Высокий",
        "label_volume": "Громкость:",
        "speed_slow": "Медленно",
        "speed_fast": "Быстро",
        "vol_low": "Тихо",
        "vol_high": "Громко",
        "chk_topic": "Читать TOPIC",
        "btn_test": "Тест",
        "btn_close": "Закрыть",
        "test_text": "Тест. Плагин TTS работает.",
        "no_voices": "Голоса не найдены",
        "device_default": "По умолчанию",
        "import_error": "pyttsx3 требуется (pip install pyttsx3)",
    },
}


def _t(key):
    try:
        import i18n
        lang = i18n.get_lang()
    except Exception:
        lang = "en"
    return _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))


def _strip_tags(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[/?b[12]\]', '', text)
    # Unicode絵文字を除去
    text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    text = re.sub(r'[\uFE00-\uFE0F]', '', text)
    # :emoji_name: 形式の絵文字を除去
    text = re.sub(r':[a-zA-Z0-9_+-]+:', '', text)
    return text.strip()


def _get_output_devices():
    devices = []
    if not _HAS_PYAUDIO:
        return devices
    try:
        p = pyaudio.PyAudio()
        default_host_api = -1
        try:
            default_host_api = p.get_default_host_api_info()['index']
        except IOError:
            pass
        for i in range(p.get_device_count()):
            try:
                info = p.get_device_info_by_index(i)
                if info['maxOutputChannels'] > 0 and (default_host_api == -1 or info['hostApi'] == default_host_api):
                    name = info['name']
                    try:
                        name = name.encode('shift-jis').decode('utf-8')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        pass
                    devices.append({"index": i, "name": name})
            except Exception:
                pass
        p.terminate()
    except Exception as e:
        logger.warning(f"[WindowsTTS] 出力デバイス取得エラー: {e}")
    return devices


class WindowsTTS(BasePlugin):
    PLUGIN_ID = "windows_tts"
    PLUGIN_NAME = "Windows TTS"
    PLUGIN_TYPE = "TOOL"

    def __init__(self):
        super().__init__()
        self._panel = None
        self._speak_queue = deque(maxlen=10)
        self._engine_lock = threading.Lock()

        saved = self.get_settings()
        self._enabled = saved.get("enabled", False)
        self._voice_id = saved.get("voice_id", "")
        self._device_index = saved.get("device_index", -1)
        self._speed = saved.get("speed", 200)      # pyttsx3: words per minute (default ~200)
        self._pitch = saved.get("pitch", 0)        # SAPI5 XML: -10 ~ +10
        self._volume = saved.get("volume", 100)     # 0-100 (UI表示用、pyttsx3には0.0-1.0で渡す)
        self._read_topic = saved.get("read_topic", False)

        self._voices = []
        self._output_devices = []

        # 読み上げワーカー起動
        self._worker_running = True
        self._speak_thread = threading.Thread(target=self._speak_worker, daemon=True)
        self._speak_thread.start()

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "voice_id": "",
            "device_index": -1,
            "speed": 200,
            "pitch": 0,
            "volume": 100,
            "read_topic": False,
        }

    def start(self, prompt_config, message_queue):
        pass

    def stop(self):
        pass

    # --------------------------------------------------------
    # テロップ出力フック
    # --------------------------------------------------------
    def on_telop_output(self, topic, main, window, layout, badge):
        if not self._enabled or not main or not _HAS_PYTTSX3:
            return
        clean_main = _strip_tags(main)
        if not clean_main:
            return

        if self._read_topic:
            clean_topic = _strip_tags(topic)
            text = f"{clean_topic}。{clean_main}" if clean_topic else clean_main
        else:
            text = clean_main

        self._speak_queue.append(text)

    # --------------------------------------------------------
    # 読み上げワーカー
    # --------------------------------------------------------
    def _speak_worker(self):
        while self._worker_running:
            if self._speak_queue:
                text = self._speak_queue.popleft()
                self._speak_text(text)
            else:
                time.sleep(0.1)

    def _speak_text(self, text):
        """pyttsx3でWAV生成 → pyaudioで指定デバイスに再生"""
        wav_path = None
        try:
            fd, wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            # pyttsx3でWAVファイルに出力（スレッドセーフのためロック）
            with self._engine_lock:
                engine = pyttsx3.init()
                if self._voice_id:
                    engine.setProperty('voice', self._voice_id)
                engine.setProperty('rate', self._speed)
                engine.setProperty('volume', self._volume / 100.0)
                # ピッチ調整（SAPI5 XMLタグ）
                if self._pitch != 0:
                    tts_text = f'<pitch absmiddle="{self._pitch}"/>{text}'
                else:
                    tts_text = text
                engine.save_to_file(tts_text, wav_path)
                engine.runAndWait()
                engine.stop()

            if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
                return

            self._play_wav(wav_path)

        except Exception as e:
            logger.warning(f"[WindowsTTS] 読み上げエラー: {e}")
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

    def _play_wav(self, wav_path):
        """WAVファイルをpyaudioで指定デバイスに再生"""
        if not _HAS_PYAUDIO:
            return

        p = None
        stream = None
        wf = None
        try:
            wf = wave.open(wav_path, 'rb')
            sample_width = wf.getsampwidth()
            channels = wf.getnchannels()
            rate = wf.getframerate()

            # WAV全体をメモリに先読み
            all_data = wf.readframes(wf.getnframes())
            wf.close()
            wf = None

            p = pyaudio.PyAudio()

            buffer_frames = 4096
            kwargs = {
                "format": p.get_format_from_width(sample_width),
                "channels": channels,
                "rate": rate,
                "output": True,
                "frames_per_buffer": buffer_frames,
            }
            if self._device_index >= 0:
                kwargs["output_device_index"] = self._device_index

            stream = p.open(**kwargs)

            bytes_per_frame = sample_width * channels
            chunk_bytes = buffer_frames * bytes_per_frame
            offset = 0
            while offset < len(all_data):
                chunk = all_data[offset:offset + chunk_bytes]
                stream.write(chunk)
                offset += chunk_bytes

            time.sleep(0.05)

        except Exception as e:
            logger.warning(f"[WindowsTTS] WAV再生エラー: {e}")
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            if p:
                try:
                    p.terminate()
                except Exception:
                    pass
            if wf:
                try:
                    wf.close()
                except Exception:
                    pass

    # --------------------------------------------------------
    # 設定UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if not _HAS_PYTTSX3:
            from tkinter import messagebox
            messagebox.showerror("Error", _t("import_error"))
            return

        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("panel_title"))
        self._panel.geometry("420x440")
        self._panel.minsize(400, 420)
        self._panel.attributes("-topmost", True)

        main_f = ttk.Frame(self._panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # ON/OFF
        self._var_enabled = tk.BooleanVar(value=self._enabled)
        def _on_enabled(*_):
            self._enabled = self._var_enabled.get()
        self._var_enabled.trace_add("write", _on_enabled)
        ttk.Checkbutton(main_f, text=_t("chk_enabled"), variable=self._var_enabled).pack(anchor="w", pady=(0, 8))

        # 音声設定
        lf = ttk.LabelFrame(main_f, text=_t("lf_voice"), padding=10)
        lf.pack(fill=tk.X, pady=(0, 10))

        # 音声一覧（pyttsx3から取得）
        if not self._voices:
            try:
                engine = pyttsx3.init()
                self._voices = engine.getProperty('voices')
                engine.stop()
            except Exception:
                self._voices = []

        ttk.Label(lf, text=_t("label_voice")).pack(anchor="w")
        voice_display = [v.name for v in self._voices]
        current_voice_name = ""
        for v in self._voices:
            if v.id == self._voice_id:
                current_voice_name = v.name
                break
        if not current_voice_name and voice_display:
            current_voice_name = voice_display[0]
            self._voice_id = self._voices[0].id

        self._var_voice = tk.StringVar(value=current_voice_name)
        if voice_display:
            combo = ttk.Combobox(lf, textvariable=self._var_voice, values=voice_display, state="readonly")
            combo.pack(fill=tk.X, pady=(0, 8))
            def _on_voice(*_):
                name = self._var_voice.get()
                for v in self._voices:
                    if v.name == name:
                        self._voice_id = v.id
                        break
            self._var_voice.trace_add("write", _on_voice)
        else:
            ttk.Label(lf, text=_t("no_voices"), foreground="red").pack(anchor="w", pady=(0, 8))

        # 再生デバイス
        if not self._output_devices:
            self._output_devices = _get_output_devices()

        ttk.Label(lf, text=_t("label_device")).pack(anchor="w")
        device_display = [_t("device_default")] + [f"{d['index']}: {d['name']}" for d in self._output_devices]

        current_device_display = _t("device_default")
        if self._device_index >= 0:
            for d in self._output_devices:
                if d["index"] == self._device_index:
                    current_device_display = f"{d['index']}: {d['name']}"
                    break

        self._var_device = tk.StringVar(value=current_device_display)
        device_combo = ttk.Combobox(lf, textvariable=self._var_device, values=device_display, state="readonly")
        device_combo.pack(fill=tk.X, pady=(0, 8))

        def _on_device(*_):
            val = self._var_device.get()
            if val == _t("device_default"):
                self._device_index = -1
            else:
                try:
                    self._device_index = int(val.split(":")[0])
                except ValueError:
                    self._device_index = -1
        self._var_device.trace_add("write", _on_device)

        # 速度 (pyttsx3: words per minute, 100-300が実用範囲)
        speed_f = ttk.Frame(lf)
        speed_f.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(speed_f, text=_t("label_speed")).pack(side="left")
        ttk.Label(speed_f, text=_t("speed_slow"), foreground="gray", font=("", 8)).pack(side="left", padx=(5, 0))
        self._var_speed = tk.IntVar(value=self._speed)
        ttk.Scale(speed_f, from_=100, to=350, variable=self._var_speed, orient="horizontal").pack(side="left", fill=tk.X, expand=True, padx=5)
        ttk.Label(speed_f, text=_t("speed_fast"), foreground="gray", font=("", 8)).pack(side="left")
        def _on_speed(*_):
            self._speed = self._var_speed.get()
        self._var_speed.trace_add("write", _on_speed)

        # ピッチ (SAPI5 XML: -10 ~ +10)
        pitch_f = ttk.Frame(lf)
        pitch_f.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(pitch_f, text=_t("label_pitch")).pack(side="left")
        ttk.Label(pitch_f, text=_t("pitch_low"), foreground="gray", font=("", 8)).pack(side="left", padx=(5, 0))
        self._var_pitch = tk.IntVar(value=self._pitch)
        ttk.Scale(pitch_f, from_=-10, to=10, variable=self._var_pitch, orient="horizontal").pack(side="left", fill=tk.X, expand=True, padx=5)
        ttk.Label(pitch_f, text=_t("pitch_high"), foreground="gray", font=("", 8)).pack(side="left")
        def _on_pitch(*_):
            self._pitch = self._var_pitch.get()
        self._var_pitch.trace_add("write", _on_pitch)

        # 音量
        vol_f = ttk.Frame(lf)
        vol_f.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(vol_f, text=_t("label_volume")).pack(side="left")
        ttk.Label(vol_f, text=_t("vol_low"), foreground="gray", font=("", 8)).pack(side="left", padx=(5, 0))
        self._var_volume = tk.IntVar(value=self._volume)
        ttk.Scale(vol_f, from_=0, to=100, variable=self._var_volume, orient="horizontal").pack(side="left", fill=tk.X, expand=True, padx=5)
        ttk.Label(vol_f, text=_t("vol_high"), foreground="gray", font=("", 8)).pack(side="left")
        def _on_volume(*_):
            self._volume = self._var_volume.get()
        self._var_volume.trace_add("write", _on_volume)

        # TOPIC読み上げ
        self._var_topic = tk.BooleanVar(value=self._read_topic)
        def _on_topic(*_):
            self._read_topic = self._var_topic.get()
        self._var_topic.trace_add("write", _on_topic)
        ttk.Checkbutton(lf, text=_t("chk_topic"), variable=self._var_topic).pack(anchor="w", pady=(5, 0))

        # テストボタン
        tk.Button(main_f, text=_t("btn_test"), bg="#17a2b8", fg="white",
                  font=("", 10, "bold"), command=self._test_speak).pack(fill=tk.X, pady=(0, 5))

        # 閉じるボタン
        tk.Button(main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
                  font=("", 10, "bold"), command=self._save_and_close).pack(fill=tk.X)

        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

    def _test_speak(self):
        self._speak_queue.append(_t("test_text"))

    def _save_and_close(self):
        settings = self.get_settings()
        settings["enabled"] = self._enabled
        settings["voice_id"] = self._voice_id
        settings["device_index"] = self._device_index
        settings["speed"] = self._speed
        settings["pitch"] = self._pitch
        settings["volume"] = self._volume
        settings["read_topic"] = self._read_topic
        self.save_settings(settings)
        self._panel.destroy()

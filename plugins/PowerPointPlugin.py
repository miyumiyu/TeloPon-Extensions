"""
PowerPointPlugin v1.00 - PowerPoint プレゼン操作プラグイン

配信者の音声指示でPowerPointのスライドショーを操作します。
スライドの送り/戻し、特定ページへのジャンプ、画面ブラックアウト、
プレゼン開始/終了に対応。スライド切替時にタイトルとノートをAIに注入します。

必要環境:
  - Windows + Microsoft PowerPoint がインストールされていること
  - pywin32（TeloPonに同梱）
"""

import threading
import time
import tkinter as tk
from tkinter import ttk

from plugin_manager import BasePlugin
import logger

_HAS_WIN32 = True
try:
    import win32com.client
    import pythoncom
except ImportError:
    _HAS_WIN32 = False

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "PowerPoint操作",
        "panel_title": "PowerPoint操作 設定",
        "chk_enabled": "PowerPoint連携 ON",
        "lf_status": " 接続状態 ",
        "btn_connect": "PowerPointに接続",
        "btn_disconnect": "切断",
        "status_disconnected": "未接続",
        "status_connected": "接続中: {title}",
        "status_slideshow": "スライドショー中: {current}/{total}",
        "status_no_ppt": "PowerPointが見つかりません",
        "status_no_slideshow": "スライドショーが開始されていません",
        "lf_options": " オプション ",
        "chk_inject_notes": "スライドのノートをAIに注入",
        "chk_inject_title": "スライドのタイトルをAIに注入",
        "btn_test_next": "次へ（テスト）",
        "btn_test_prev": "前へ（テスト）",
        "btn_close": "閉じる",
        "no_win32": "pywin32が必要です",
        "note_cue": "【プレゼン資料のカンペ】\nスライド {current}/{total}: {title}\n{notes}",
        "note_cue_no_notes": "【プレゼン資料のカンペ】\nスライド {current}/{total}: {title}",
    },
    "en": {
        "plugin_name": "PowerPoint Control",
        "panel_title": "PowerPoint Control Settings",
        "chk_enabled": "PowerPoint Integration ON",
        "lf_status": " Connection Status ",
        "btn_connect": "Connect to PowerPoint",
        "btn_disconnect": "Disconnect",
        "status_disconnected": "Not connected",
        "status_connected": "Connected: {title}",
        "status_slideshow": "Slideshow: {current}/{total}",
        "status_no_ppt": "PowerPoint not found",
        "status_no_slideshow": "No slideshow running",
        "lf_options": " Options ",
        "chk_inject_notes": "Inject slide notes to AI",
        "chk_inject_title": "Inject slide title to AI",
        "btn_test_next": "Next (Test)",
        "btn_test_prev": "Previous (Test)",
        "btn_close": "Close",
        "no_win32": "pywin32 required",
        "note_cue": "[Presentation Notes]\nSlide {current}/{total}: {title}\n{notes}",
        "note_cue_no_notes": "[Presentation Notes]\nSlide {current}/{total}: {title}",
    },
    "ko": {
        "plugin_name": "PowerPoint 조작",
        "panel_title": "PowerPoint 조작 설정",
        "chk_enabled": "PowerPoint 연동 ON",
        "lf_status": " 연결 상태 ",
        "btn_connect": "PowerPoint에 연결",
        "btn_disconnect": "연결 끊기",
        "status_disconnected": "미연결",
        "status_connected": "연결됨: {title}",
        "status_slideshow": "슬라이드쇼: {current}/{total}",
        "status_no_ppt": "PowerPoint를 찾을 수 없습니다",
        "status_no_slideshow": "슬라이드쇼가 실행되지 않음",
        "lf_options": " 옵션 ",
        "chk_inject_notes": "슬라이드 노트를 AI에 주입",
        "chk_inject_title": "슬라이드 제목을 AI에 주입",
        "btn_test_next": "다음 (테스트)",
        "btn_test_prev": "이전 (테스트)",
        "btn_close": "닫기",
        "no_win32": "pywin32 필요",
        "note_cue": "[프레젠테이션 노트]\n슬라이드 {current}/{total}: {title}\n{notes}",
        "note_cue_no_notes": "[프레젠테이션 노트]\n슬라이드 {current}/{total}: {title}",
    },
    "ru": {
        "plugin_name": "Управление PowerPoint",
        "panel_title": "Настройки PowerPoint",
        "chk_enabled": "PowerPoint ВКЛ",
        "lf_status": " Состояние ",
        "btn_connect": "Подключить к PowerPoint",
        "btn_disconnect": "Отключить",
        "status_disconnected": "Не подключено",
        "status_connected": "Подключено: {title}",
        "status_slideshow": "Слайд-шоу: {current}/{total}",
        "status_no_ppt": "PowerPoint не найден",
        "status_no_slideshow": "Слайд-шоу не запущено",
        "lf_options": " Опции ",
        "chk_inject_notes": "Передавать заметки слайда ИИ",
        "chk_inject_title": "Передавать заголовок слайда ИИ",
        "btn_test_next": "Далее (Тест)",
        "btn_test_prev": "Назад (Тест)",
        "btn_close": "Закрыть",
        "no_win32": "Требуется pywin32",
        "note_cue": "[Заметки презентации]\nСлайд {current}/{total}: {title}\n{notes}",
        "note_cue_no_notes": "[Заметки презентации]\nСлайд {current}/{total}: {title}",
    },
}


def _t(key, **kwargs):
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


class PowerPointPlugin(BasePlugin):
    PLUGIN_ID = "powerpoint_ctrl"
    PLUGIN_NAME = "PowerPoint Control"
    PLUGIN_TYPE = "TOOL"

    # CMD ハイブリッド: [CMD]PPT:xxx
    IDENTIFIER = "PPT"

    def __init__(self):
        super().__init__()
        self._panel = None
        self.plugin_queue = None
        self.is_running = False

        self._ppt_app = None
        self._presentation = None
        self._slideshow_view = None
        self._last_slide_num = -1
        self._monitor_thread = None
        self._monitoring = False

        saved = self.get_settings()
        self._enabled = saved.get("enabled", False)
        self._inject_notes = saved.get("inject_notes", True)
        self._inject_title = saved.get("inject_title", True)

    def get_display_name(self):
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "inject_notes": True,
            "inject_title": True,
        }

    # --------------------------------------------------------
    # PowerPoint COM接続
    # --------------------------------------------------------
    def _connect_ppt(self):
        """実行中のPowerPointに接続"""
        if not _HAS_WIN32:
            return False
        try:
            pythoncom.CoInitialize()
            self._ppt_app = win32com.client.GetActiveObject("PowerPoint.Application")
            if self._ppt_app.Presentations.Count > 0:
                self._presentation = self._ppt_app.ActivePresentation
                logger.info(f"[{self.PLUGIN_NAME}] PowerPoint接続: {self._presentation.Name}")
                return True
            else:
                logger.warning(f"[{self.PLUGIN_NAME}] プレゼンテーションが開かれていません")
                return False
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] PowerPoint接続失敗: {e}")
            self._ppt_app = None
            self._presentation = None
            return False

    def _get_slideshow_view(self):
        """スライドショーのViewオブジェクトを取得"""
        try:
            if self._ppt_app and self._ppt_app.SlideShowWindows.Count > 0:
                self._slideshow_view = self._ppt_app.SlideShowWindows(1).View
                return self._slideshow_view
        except Exception:
            pass
        self._slideshow_view = None
        return None

    def _disconnect_ppt(self):
        """PowerPointから切断"""
        self._monitoring = False
        self._ppt_app = None
        self._presentation = None
        self._slideshow_view = None
        self._last_slide_num = -1

    def _get_slide_info(self, slide_num):
        """指定スライドのタイトルとノートを取得"""
        title = ""
        notes = ""
        try:
            slide = self._presentation.Slides(slide_num)
            try:
                title = slide.Shapes.Title.TextFrame.TextRange.Text
            except Exception:
                title = f"Slide {slide_num}"
            try:
                notes = slide.NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.Text
            except Exception:
                pass
        except Exception:
            pass
        return title, notes

    def _get_total_slides(self):
        try:
            return self._presentation.Slides.Count
        except Exception:
            return 0

    def _get_current_slide_num(self):
        try:
            ssv = self._get_slideshow_view()
            if ssv:
                return ssv.CurrentShowPosition
        except Exception:
            pass
        return 0

    # --------------------------------------------------------
    # スライド変更の監視 + AI注入
    # --------------------------------------------------------
    def _start_monitoring(self):
        """スライド変更を監視してAIにノートを注入"""
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        """スライド番号を定期チェックし、変更があればAI注入"""
        pythoncom.CoInitialize()
        while self._monitoring and self.is_running:
            try:
                current = self._get_current_slide_num()
                if current > 0 and current != self._last_slide_num:
                    self._last_slide_num = current
                    self._on_slide_changed(current)
                    # UI更新
                    if self._panel and self._panel.winfo_exists():
                        total = self._get_total_slides()
                        self._panel.after(0, lambda: self._update_status_label(
                            _t("status_slideshow", current=current, total=total), "green"
                        ))
            except Exception:
                pass
            time.sleep(0.5)

    def _on_slide_changed(self, slide_num):
        """スライドが変わったらAIに情報を注入"""
        if not self.plugin_queue:
            return

        title, notes = self._get_slide_info(slide_num)
        total = self._get_total_slides()

        if self._inject_notes and notes:
            cue = _t("note_cue", current=slide_num, total=total, title=title, notes=notes)
        elif self._inject_title:
            cue = _t("note_cue_no_notes", current=slide_num, total=total, title=title)
        else:
            return

        self.send_text(self.plugin_queue, cue)
        logger.info(f"[{self.PLUGIN_NAME}] スライド{slide_num}/{total}: {title[:30]}")

    # --------------------------------------------------------
    # プラグイン ライフサイクル
    # --------------------------------------------------------
    def get_prompt_addon(self):
        if not self._enabled or not self._ppt_app:
            return ""
        return (
            "\n# 【PowerPoint操作コマンド】\n"
            "配信者の指示でスライドを操作できます。テロップの末尾（[MEMO]の直前）に記述してください。\n"
            "* 次のスライド: [CMD]PPT:next\n"
            "* 前のスライド: [CMD]PPT:prev\n"
            "* 特定のスライドへ: [CMD]PPT:goto ページ番号\n"
            "* 最初のスライド: [CMD]PPT:first\n"
            "* 最後のスライド: [CMD]PPT:last\n"
            "* プレゼン開始: [CMD]PPT:start\n"
            "* プレゼン終了: [CMD]PPT:end\n"
            "* 画面ブラックアウト: [CMD]PPT:black\n"
            "* 画面復帰: [CMD]PPT:resume\n"
            "\n## 配信者の発言に対する反応ルール\n"
            "* 「次へ」「次のスライド」「次のページ」→ [CMD]PPT:next\n"
            "* 「前に」「前のスライド」「戻って」→ [CMD]PPT:prev\n"
            "* 「○ページ目に飛んで」「○番に行って」→ [CMD]PPT:goto 番号\n"
            "* 「最初に戻って」→ [CMD]PPT:first\n"
            "* 「最後のスライド」→ [CMD]PPT:last\n"
            "* 「プレゼン始めて」→ [CMD]PPT:start\n"
            "* 「プレゼン終わり」→ [CMD]PPT:end\n"
            "* 「画面消して」「ブラックアウト」→ [CMD]PPT:black\n"
            "* 「画面戻して」→ [CMD]PPT:resume\n"
            "\n## 視聴者コメントからの実行権限\n"
            "* 配信者の音声指示のみ（視聴者コメントでは実行禁止）\n"
        )

    def start(self, prompt_config, plugin_queue):
        self.plugin_queue = plugin_queue
        self.is_running = True
        if self._enabled and self._ppt_app:
            self._start_monitoring()

    def stop(self):
        self.is_running = False
        self._monitoring = False

    # --------------------------------------------------------
    # CMD ハンドラー: [CMD]PPT:xxx
    # --------------------------------------------------------
    def setup(self, cfg) -> bool:
        return True

    def handle(self, value: str):
        if not value or not self._ppt_app:
            return

        import re
        value = re.sub(r'\[(?:WND|LAY|BDG|MEMO|TOPIC|MAIN)\].*$', '', value, flags=re.IGNORECASE).strip()
        if not value:
            return

        v_lower = value.lower()

        try:
            if v_lower.startswith("next"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.Next()
                    logger.info(f"[{self.PLUGIN_NAME}] Next")
            elif v_lower.startswith("prev"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.Previous()
                    logger.info(f"[{self.PLUGIN_NAME}] Previous")
            elif v_lower.startswith("goto"):
                num = int(value[4:].strip())
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.GotoSlide(num)
                    logger.info(f"[{self.PLUGIN_NAME}] Goto {num}")
            elif v_lower.startswith("first"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.First()
                    logger.info(f"[{self.PLUGIN_NAME}] First")
            elif v_lower.startswith("last"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.Last()
                    logger.info(f"[{self.PLUGIN_NAME}] Last")
            elif v_lower.startswith("start"):
                if self._presentation:
                    self._presentation.SlideShowSettings.Run()
                    logger.info(f"[{self.PLUGIN_NAME}] Start slideshow")
            elif v_lower.startswith("end"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.Exit()
                    logger.info(f"[{self.PLUGIN_NAME}] End slideshow")
            elif v_lower.startswith("black"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.State = 3  # ppSlideShowBlackScreen
                    logger.info(f"[{self.PLUGIN_NAME}] Black screen")
            elif v_lower.startswith("resume"):
                ssv = self._get_slideshow_view()
                if ssv:
                    ssv.State = 1  # ppSlideShowRunning
                    logger.info(f"[{self.PLUGIN_NAME}] Resume")
            else:
                logger.warning(f"[{self.PLUGIN_NAME}] 未知のサブコマンド: {value}")
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] コマンド実行エラー: {e}")

    # --------------------------------------------------------
    # 設定UI
    # --------------------------------------------------------
    def open_settings_ui(self, parent_window):
        if not _HAS_WIN32:
            from tkinter import messagebox
            messagebox.showerror("Error", _t("no_win32"))
            return

        if self._panel and self._panel.winfo_exists():
            self._panel.lift()
            return

        self._panel = tk.Toplevel(parent_window)
        self._panel.title(_t("panel_title"))
        self._panel.geometry("400x380")
        self._panel.minsize(380, 360)
        self._panel.attributes("-topmost", True)

        main_f = ttk.Frame(self._panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # ON/OFF
        self._var_enabled = tk.BooleanVar(value=self._enabled)
        def _on_enabled(*_):
            self._enabled = self._var_enabled.get()
        self._var_enabled.trace_add("write", _on_enabled)
        ttk.Checkbutton(main_f, text=_t("chk_enabled"), variable=self._var_enabled).pack(anchor="w", pady=(0, 8))

        # 接続状態
        status_f = ttk.LabelFrame(main_f, text=_t("lf_status"), padding=10)
        status_f.pack(fill=tk.X, pady=(0, 8))

        self._lbl_status = ttk.Label(status_f, text=_t("status_disconnected"), foreground="gray")
        self._lbl_status.pack(anchor="w", pady=(0, 5))

        btn_f = ttk.Frame(status_f)
        btn_f.pack(fill=tk.X)
        tk.Button(btn_f, text=_t("btn_connect"), bg="#007bff", fg="white",
                  font=("", 9, "bold"), command=self._on_connect).pack(side="left", padx=(0, 5))
        tk.Button(btn_f, text=_t("btn_disconnect"), font=("", 9),
                  command=self._on_disconnect).pack(side="left")

        # オプション
        opt_f = ttk.LabelFrame(main_f, text=_t("lf_options"), padding=10)
        opt_f.pack(fill=tk.X, pady=(0, 8))

        self._var_notes = tk.BooleanVar(value=self._inject_notes)
        def _on_notes(*_):
            self._inject_notes = self._var_notes.get()
        self._var_notes.trace_add("write", _on_notes)
        ttk.Checkbutton(opt_f, text=_t("chk_inject_notes"), variable=self._var_notes).pack(anchor="w", pady=1)

        self._var_title = tk.BooleanVar(value=self._inject_title)
        def _on_title(*_):
            self._inject_title = self._var_title.get()
        self._var_title.trace_add("write", _on_title)
        ttk.Checkbutton(opt_f, text=_t("chk_inject_title"), variable=self._var_title).pack(anchor="w", pady=1)

        # テストボタン
        test_f = ttk.Frame(main_f)
        test_f.pack(fill=tk.X, pady=(0, 8))
        tk.Button(test_f, text=_t("btn_test_prev"), font=("", 9),
                  command=lambda: self.handle("prev")).pack(side="left", padx=(0, 5))
        tk.Button(test_f, text=_t("btn_test_next"), font=("", 9),
                  command=lambda: self.handle("next")).pack(side="left")

        # 閉じるボタン
        tk.Button(main_f, text=_t("btn_close"), bg="#6c757d", fg="white",
                  font=("", 10, "bold"), command=self._save_and_close).pack(fill=tk.X)
        self._panel.protocol("WM_DELETE_WINDOW", self._save_and_close)

        # 接続済みなら状態を表示
        if self._ppt_app and self._presentation:
            try:
                name = self._presentation.Name
                self._update_status_label(_t("status_connected", title=name), "green")
            except Exception:
                pass

    def _update_status_label(self, text, color):
        if hasattr(self, '_lbl_status') and self._lbl_status.winfo_exists():
            self._lbl_status.config(text=text, foreground=color)

    def _on_connect(self):
        if self._connect_ppt():
            name = self._presentation.Name
            self._update_status_label(_t("status_connected", title=name), "green")
            # スライドショー中ならモニタリング開始
            if self._get_slideshow_view() and self.is_running:
                self._start_monitoring()
        else:
            self._update_status_label(_t("status_no_ppt"), "red")

    def _on_disconnect(self):
        self._disconnect_ppt()
        self._update_status_label(_t("status_disconnected"), "gray")

    def _save_and_close(self):
        settings = self.get_settings()
        settings["enabled"] = self._enabled
        settings["inject_notes"] = self._inject_notes
        settings["inject_title"] = self._inject_title
        self.save_settings(settings)
        self._panel.destroy()

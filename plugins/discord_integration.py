"""
discord_integration v1.00 - Discord連携プラグイン
"""
import os
import threading
import time
import requests
import asyncio
import re
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser # ★追加: ブラウザを開くための標準ライブラリ

try:
    import discord
except ImportError:
    discord = None

from plugin_manager import BasePlugin
import logger # ★TeloPon標準ロガー

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "💬 Discord",
        "window_title": "⚙️ Discordリアルタイム連携設定",
        "err_no_lib": "⚠️ エラー: discord.py がインストールされていません。\nコマンドプロンプトで pip install discord.py を実行してください。",
        "status_disconnected": "🔌 状態: 切断中",
        "lf_conn": " Discord Bot 接続設定 ",
        "label_token": "Bot トークン:",
        "btn_invite": "🔗 このBotをサーバーに招待する (ブラウザが開きます)",
        "btn_fetch": "🔄 トークン確認 ＆ チャンネル一覧を取得",
        "fetch_hint": "トークンを入力して「取得」ボタンを押してください",
        "label_channel": "監視するチャンネル:",
        "btn_connect": "接続",
        "lf_ai": " AIへの送信設定 ",
        "label_prompt": "AIに渡す時の指示テキスト (プロンプト):",
        "btn_save": "保存して閉じる",
        "btn_cancel": "キャンセル",
        "status_connected": "⚡ 状態: 接続中 (Botが稼働しています)",
        "btn_disconnect": "切断",
        "warn_title": "警告",
        "warn_no_token_invite": "招待URLを生成するためには、まずBotトークンを入力してください。",
        "invite_generating": "🔗 招待URLを生成中...",
        "invite_success": "✅ ブラウザで招待画面を開きました！",
        "invite_err_invalid_token": "❌ 無効なトークンです。正しいトークンを入力してください。",
        "invite_err_network": "❌ 通信エラー: ",
        "warn_no_token_channel": "トークンと監視するチャンネルを指定してください。",
        "warn_no_token": "Botトークンを入力してください。",
        "fetch_loading": "📝 通信中... (サーバーとチャンネルを取得しています)",
        "fetch_err_invalid_token": "❌ 無効なトークンです (HTTP ",
        "fetch_success": "✅ 成功: Bot「{name}」として認証しました！",
        "fetch_err": "❌ エラー: ",
        "default_prompt": "【Discordからのコメント】モデレーターからの指示または視聴者のコメントです！\n",
    },
    "en": {
        "plugin_name": "💬 Discord",
        "window_title": "⚙️ Discord Realtime Integration Settings",
        "err_no_lib": "⚠️ Error: discord.py is not installed.\nRun: pip install discord.py",
        "status_disconnected": "🔌 Status: Disconnected",
        "lf_conn": " Discord Bot Connection ",
        "label_token": "Bot Token:",
        "btn_invite": "🔗 Invite this Bot to your server (opens browser)",
        "btn_fetch": "🔄 Verify Token & Fetch Channel List",
        "fetch_hint": "Enter token and press the Fetch button",
        "label_channel": "Channel to monitor:",
        "btn_connect": "Connect",
        "lf_ai": " AI Send Settings ",
        "label_prompt": "Instruction text to pass to AI (prompt):",
        "btn_save": "Save & Close",
        "btn_cancel": "Cancel",
        "status_connected": "⚡ Status: Connected (Bot is running)",
        "btn_disconnect": "Disconnect",
        "warn_title": "Warning",
        "warn_no_token_invite": "Please enter the Bot token first to generate an invite URL.",
        "invite_generating": "🔗 Generating invite URL...",
        "invite_success": "✅ Invite page opened in browser!",
        "invite_err_invalid_token": "❌ Invalid token. Please enter the correct token.",
        "invite_err_network": "❌ Network error: ",
        "warn_no_token_channel": "Please specify the token and the channel to monitor.",
        "warn_no_token": "Please enter the Bot token.",
        "fetch_loading": "📝 Connecting... (fetching servers and channels)",
        "fetch_err_invalid_token": "❌ Invalid token (HTTP ",
        "fetch_success": "✅ Success: Authenticated as Bot '{name}'!",
        "fetch_err": "❌ Error: ",
        "default_prompt": "[Discord Comment] This is a message from a moderator or viewer!\n",
    },
    "ru": {
        "plugin_name": "💬 Discord",
        "window_title": "⚙️ Настройки Discord Realtime",
        "err_no_lib": "⚠️ Ошибка: discord.py не установлен.\nВыполните: pip install discord.py",
        "status_disconnected": "🔌 Статус: Отключено",
        "lf_conn": " Подключение Discord Bot ",
        "label_token": "Bot Token:",
        "btn_invite": "🔗 Пригласить Bot на сервер (откроется браузер)",
        "btn_fetch": "🔄 Проверить токен и получить список каналов",
        "fetch_hint": "Введите токен и нажмите «Получить»",
        "label_channel": "Канал для мониторинга:",
        "btn_connect": "Подключить",
        "lf_ai": " Настройки отправки ИИ ",
        "label_prompt": "Текст инструкции для ИИ (промпт):",
        "btn_save": "Сохранить и закрыть",
        "btn_cancel": "Отмена",
        "status_connected": "⚡ Статус: Подключено (Bot запущен)",
        "btn_disconnect": "Отключить",
        "warn_title": "Предупреждение",
        "warn_no_token_invite": "Сначала введите Bot токен для создания ссылки приглашения.",
        "invite_generating": "🔗 Генерация ссылки приглашения...",
        "invite_success": "✅ Страница приглашения открыта в браузере!",
        "invite_err_invalid_token": "❌ Неверный токен. Введите правильный токен.",
        "invite_err_network": "❌ Ошибка сети: ",
        "warn_no_token_channel": "Укажите токен и канал для мониторинга.",
        "warn_no_token": "Введите Bot токен.",
        "fetch_loading": "📝 Подключение... (получение серверов и каналов)",
        "fetch_err_invalid_token": "❌ Неверный токен (HTTP ",
        "fetch_success": "✅ Успех: Авторизован как Bot '{name}'!",
        "fetch_err": "❌ Ошибка: ",
        "default_prompt": "[Комментарий Discord] Это сообщение от модератора или зрителя!\n",
    },
    "ko": {
        "plugin_name": "💬 Discord",
        "window_title": "⚙️ Discord 실시간 연동 설정",
        "err_no_lib": "⚠️ 오류: discord.py가 설치되어 있지 않습니다.\n실행하세요: pip install discord.py",
        "status_disconnected": "🔌 상태: 연결 끊김",
        "lf_conn": " Discord Bot 연결 ",
        "label_token": "Bot 토큰:",
        "btn_invite": "🔗 이 Bot을 서버에 초대 (브라우저 열림)",
        "btn_fetch": "🔄 토큰 확인 & 채널 목록 가져오기",
        "fetch_hint": "토큰을 입력하고 가져오기 버튼을 누르세요",
        "label_channel": "모니터링할 채널:",
        "btn_connect": "연결",
        "lf_ai": " AI 전송 설정 ",
        "label_prompt": "AI에 전달할 지시 텍스트 (프롬프트):",
        "btn_save": "저장 후 닫기",
        "btn_cancel": "취소",
        "status_connected": "⚡ 상태: 연결됨 (Bot 실행 중)",
        "btn_disconnect": "연결 끊기",
        "warn_title": "경고",
        "warn_no_token_invite": "초대 URL 생성을 위해 먼저 Bot 토큰을 입력하세요.",
        "invite_generating": "🔗 초대 URL 생성 중...",
        "invite_success": "✅ 브라우저에서 초대 페이지가 열렸습니다!",
        "invite_err_invalid_token": "❌ 잘못된 토큰입니다. 올바른 토큰을 입력하세요.",
        "invite_err_network": "❌ 네트워크 오류: ",
        "warn_no_token_channel": "토큰과 모니터링할 채널을 지정하세요.",
        "warn_no_token": "Bot 토큰을 입력하세요.",
        "fetch_loading": "📝 연결 중... (서버 및 채널 가져오는 중)",
        "fetch_err_invalid_token": "❌ 잘못된 토큰 (HTTP ",
        "fetch_success": "✅ 성공: Bot '{name}'으로 인증됨!",
        "fetch_err": "❌ 오류: ",
        "default_prompt": "[Discord 댓글] 모더레이터 또는 시청자의 메시지입니다!\n",
    },
}

def _t(key, **kwargs):
    try:
        import i18n
        lang = i18n.get_lang()
    except Exception:
        lang = "en"
    text = _L.get(lang, _L["en"]).get(key, _L["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text

class DiscordRealtimePlugin(BasePlugin):
    PLUGIN_ID = "discord_realtime"
    PLUGIN_NAME = "Discordリアルタイム連携"
    PLUGIN_VERSION = "1.00"
    PLUGIN_TYPE = "TOOL"

    def get_display_name(self):
        return _t("plugin_name")

    def __init__(self):
        super().__init__()
        self.plugin_queue = None
        self.is_running = False
        self.is_connected = False # UI・システム連動の接続フラグ

        # 非同期処理（Discord通信）用の変数
        self.loop_thread = None
        self.loop = None
        self.client = None

        # チャンネルの「表示名」と「裏のID」を紐付ける辞書
        self.channel_map = {}

    def get_default_settings(self):
        return {
            "enabled": False,          # ON/OFFフラグ（接続状態）
            "discord_token": "",       # Botトークン
            "channel_id": "",          # 監視するチャンネルID（裏側用）
            "channel_name": "",        # 監視するチャンネルの表示名（UI用）
            "prompt_text": _t("default_prompt")
        }

    # ==========================================
    # ⚙️ 設定UIの構築
    # ==========================================
    def open_settings_ui(self, parent_window):
        if hasattr(self, "panel") and self.panel is not None and self.panel.winfo_exists():
            self.panel.lift()
            return

        self.panel = tk.Toplevel(parent_window)
        self.panel.title(_t("window_title"))
        self.panel.geometry("480x560")
        self.panel.attributes("-topmost", True)

        if discord is None:
            lbl_err = tk.Label(self.panel, text=_t("err_no_lib"), fg="red", bg="#ffe6e6", pady=10)
            lbl_err.pack(fill=tk.X)

        settings = self.get_settings()
        self.is_connected = settings.get("enabled", False)

        main_f = ttk.Frame(self.panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        # --- 1. 一番上の状態表示メッセージ ---
        self.lbl_top_status = ttk.Label(main_f, text=_t("status_disconnected"), font=("", 11, "bold"), foreground="gray")
        self.lbl_top_status.pack(anchor="w", pady=(0, 15))

        # --- Discord API 接続設定 ---
        lf_conn = ttk.LabelFrame(main_f, text=_t("lf_conn"), padding=10)
        lf_conn.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(lf_conn, text=_t("label_token")).pack(anchor="w")
        self.ent_token = ttk.Entry(lf_conn, show="*")
        self.ent_token.pack(fill=tk.X, pady=(0, 5))
        self.ent_token.insert(0, settings.get("discord_token", ""))

        self.btn_invite = tk.Button(lf_conn, text=_t("btn_invite"), bg="#2c2f33", fg="white", font=("", 9), command=self._open_invite_link)
        self.btn_invite.pack(fill=tk.X, pady=(0, 10))

        self.btn_fetch = tk.Button(lf_conn, text=_t("btn_fetch"), bg="#5865F2", fg="white", font=("", 9, "bold"), command=self._fetch_channels)
        self.btn_fetch.pack(fill=tk.X, pady=(0, 5))

        self.lbl_test_result = ttk.Label(lf_conn, text=_t("fetch_hint"), foreground="#555")
        self.lbl_test_result.pack(anchor="w", pady=(0, 10))

        ttk.Label(lf_conn, text=_t("label_channel")).pack(anchor="w")

        self.cmb_channel = ttk.Combobox(lf_conn, state="readonly")
        self.cmb_channel.pack(fill=tk.X, pady=(0, 10))

        display_val = settings.get("channel_name", settings.get("channel_id", ""))
        self.cmb_channel.set(display_val)

        # 接続/切断ボタン
        self.btn_connect = tk.Button(lf_conn, text=_t("btn_connect"), bg="#007bff", fg="white", font=("", 10, "bold"), command=self._toggle_connection)
        self.btn_connect.pack(fill=tk.X, pady=(5, 0))

        # --- AI送信設定 ---
        lf_ai = ttk.LabelFrame(main_f, text=_t("lf_ai"), padding=10)
        lf_ai.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(lf_ai, text=_t("label_prompt")).pack(anchor="w")
        self.txt_prompt = tk.Text(lf_ai, height=3, font=("", 10))
        self.txt_prompt.pack(fill=tk.X)
        self.txt_prompt.insert(tk.END, settings.get("prompt_text", ""))

        # --- 保存・キャンセルボタン ---
        btn_f = ttk.Frame(main_f)
        btn_f.pack(fill=tk.X, pady=(5, 0))
        tk.Button(btn_f, text=_t("btn_save"), bg="#007bff", fg="white", font=("", 10, "bold"), command=self._save_and_close).pack(side="left", expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(btn_f, text=_t("btn_cancel"), bg="#6c757d", fg="white", command=self.panel.destroy).pack(side="right", expand=True, fill=tk.X, padx=(5, 0))

        self._update_ui_state()

    def _update_ui_state(self):
        """接続状態に合わせてUI（文字とボタンの色・ロック状態）を切り替える"""
        if not hasattr(self, 'btn_connect') or not self.btn_connect.winfo_exists(): return

        if self.is_connected:
            self.lbl_top_status.config(text=_t("status_connected"), foreground="#28a745")
            self.btn_connect.config(text=_t("btn_disconnect"), bg="#dc3545")
            self.ent_token.config(state="readonly")
            self.cmb_channel.config(state="disabled")
            self.btn_fetch.config(state="disabled")
            self.btn_invite.config(state="disabled")
        else:
            self.lbl_top_status.config(text=_t("status_disconnected"), foreground="gray")
            self.btn_connect.config(text=_t("btn_connect"), bg="#007bff")
            self.ent_token.config(state="normal")
            self.cmb_channel.config(state="readonly")
            self.btn_fetch.config(state="normal")
            self.btn_invite.config(state="normal")

    def _open_invite_link(self):
        token = self.ent_token.get().strip()
        if not token:
            messagebox.showwarning(_t("warn_title"), _t("warn_no_token_invite"))
            return

        self.lbl_test_result.config(text=_t("invite_generating"), foreground="blue")
        self.panel.update()

        def fetch_and_open():
            headers = {"Authorization": f"Bot {token}"}
            try:
                res = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
                if res.status_code == 200:
                    bot_id = res.json().get("id")
                    url = f"https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=66560&integration_type=0&scope=bot"
                    self.panel.after(0, lambda: self.lbl_test_result.config(text=_t("invite_success"), foreground="green"))
                    webbrowser.open(url)
                else:
                    self.panel.after(0, lambda: self.lbl_test_result.config(text=_t("invite_err_invalid_token"), foreground="red"))
            except Exception as e:
                self.panel.after(0, lambda: self.lbl_test_result.config(text=_t("invite_err_network") + str(e)[:30], foreground="red"))

        threading.Thread(target=fetch_and_open, daemon=True).start()

    def _toggle_connection(self):
        if self.is_connected:
            self.is_connected = False
            self._update_ui_state()
            self._save_settings_from_ui()
            self._stop_bot()
        else:
            token = self.ent_token.get().strip()
            raw_channel = self.cmb_channel.get().strip()

            if not token or not raw_channel:
                messagebox.showwarning(_t("warn_title"), _t("warn_no_token_channel"))
                return

            self.is_connected = True
            self._update_ui_state()
            self._save_settings_from_ui()
            self._start_bot()

    def _fetch_channels(self):
        token = self.ent_token.get().strip()
        if not token:
            messagebox.showwarning(_t("warn_title"), _t("warn_no_token"))
            return

        self.lbl_test_result.config(text=_t("fetch_loading"), foreground="blue")
        self.btn_fetch.config(state="disabled")
        self.panel.update()

        def fetch_task():
            headers = {"Authorization": f"Bot {token}"}
            try:
                res = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
                if res.status_code != 200:
                    self.panel.after(0, lambda: self._fetch_done(_t("fetch_err_invalid_token") + f"{res.status_code})", None, None))
                    return

                bot_name = res.json().get("username", "Unknown")
                guilds_res = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers, timeout=5)

                channels_list = []
                temp_map = {}

                type_icons = {0: "💬", 2: "🔊", 5: "📢"}

                if guilds_res.status_code == 200:
                    for g in guilds_res.json():
                        g_id = g["id"]
                        g_name = g["name"]
                        ch_res = requests.get(f"https://discord.com/api/v10/guilds/{g_id}/channels", headers=headers, timeout=5)
                        if ch_res.status_code == 200:
                            for ch in ch_res.json():
                                c_type = ch.get("type")
                                if c_type in [0, 2, 5]:
                                    icon = type_icons.get(c_type, "💬")
                                    display_name = f"{icon} {g_name} / {ch['name']}"
                                    while display_name in temp_map:
                                        display_name += " "
                                    channels_list.append(display_name)
                                    temp_map[display_name] = str(ch["id"])

                self.panel.after(0, lambda: self._fetch_done(_t("fetch_success", name=bot_name), channels_list, temp_map))
            except Exception as e:
                self.panel.after(0, lambda: self._fetch_done(_t("fetch_err") + str(e)[:30], None, None))

        threading.Thread(target=fetch_task, daemon=True).start()

    def _fetch_done(self, msg, channels_list, temp_map):
        if not hasattr(self, 'panel') or not self.panel.winfo_exists(): return
        self.btn_fetch.config(state="normal")
        self.lbl_test_result.config(text=msg, foreground="green" if "✅" in msg else "red")

        if channels_list is not None and temp_map is not None:
            self.channel_map = temp_map
            self.cmb_channel.config(state="readonly")
            self.cmb_channel['values'] = channels_list
            if not self.cmb_channel.get() or self.cmb_channel.get() not in channels_list:
                self.cmb_channel.set(channels_list[0])
            if self.is_connected:
                self.cmb_channel.config(state="disabled")

    def _save_settings_from_ui(self):
        settings = self.get_settings()
        settings["enabled"] = self.is_connected
        settings["discord_token"] = self.ent_token.get().strip()
        settings["prompt_text"] = self.txt_prompt.get("1.0", tk.END).strip()

        raw_channel = self.cmb_channel.get()
        if raw_channel in self.channel_map:
            settings["channel_id"] = self.channel_map[raw_channel]
            settings["channel_name"] = raw_channel.strip()

        self.save_settings(settings)

    def _save_and_close(self):
        self._save_settings_from_ui()
        self.panel.destroy()

    # ==========================================
    # 🧠 AI連携 & Bot起動ロジック
    # ==========================================
    def start(self, prompt_config, plugin_queue):
        self.plugin_queue = plugin_queue
        if self.is_connected:
            self._start_bot()

    def stop(self):
        self.plugin_queue = None

    def _start_bot(self):
        if discord is None:
            logger.error(f"[{self.PLUGIN_NAME}] ❌ discord.py がインストールされていません。")
            return

        self.is_running = True
        if self.loop_thread is not None and self.loop_thread.is_alive():
            return

        self.loop_thread = threading.Thread(target=self._run_discord_bot, daemon=True)
        self.loop_thread.start()
        logger.info(f"[{self.PLUGIN_NAME}] ▶️ Discord WebSocket通信を開始します...")

    def _stop_bot(self):
        self.is_running = False
        if self.client and not self.client.is_closed() and self.loop:
            asyncio.run_coroutine_threadsafe(self.client.close(), self.loop)
        logger.info(f"[{self.PLUGIN_NAME}] ⏹️ Discord連携を停止しました。")

    def _run_discord_bot(self):
        settings = self.get_settings()
        token = settings.get("discord_token", "").strip()
        channel_id_str = settings.get("channel_id", "").strip()
        prompt_prefix = settings.get("prompt_text", _t("default_prompt"))

        if not token or not channel_id_str:
            logger.warning(f"[{self.PLUGIN_NAME}] ⚠️ トークンまたはチャンネルIDが未設定のため、起動をスキップしました。")
            return

        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()

        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            logger.info(f"[{self.PLUGIN_NAME}] ✅ ログイン完了: {self.client.user.name} (監視ID: {channel_id_str})")

        @self.client.event
        async def on_message(message):
            if message.author.bot: return
            if str(message.channel.id) != channel_id_str: return

            content = message.content.strip()
            if not content: return

            # アバターをCoreに送信
            display_name = message.author.display_name
            try:
                avatar_url = str(message.author.display_avatar.url) if message.author.display_avatar else ""
                if avatar_url and self.plugin_queue:
                    self.send_avatar_map(self.plugin_queue, {display_name: avatar_url})
                    logger.debug(f"[Avatar] Discord取得: {display_name} → {avatar_url[:40]}")
            except Exception:
                pass

            final_text = f"[COMMENT] {display_name}: {content}\n\n{prompt_prefix}"

            if self.plugin_queue:
                self.send_text(self.plugin_queue, final_text)
                logger.info(f"[{self.PLUGIN_NAME}] ⚡ リアルタイム受信: {message.author.display_name}のコメントをAIに即時送信しました！")
            else:
                logger.debug(f"[{self.PLUGIN_NAME}] メッセージを受信しましたが、TeloPonが待機中のためスキップしました。")

        try:
            self.loop.run_until_complete(self.client.start(token))
        except Exception as e:
            if self.is_running:
                logger.warning(f"[{self.PLUGIN_NAME}] ⚠️ 予期せぬ切断: {e}")

"""
slack_integration v1.00 - Slack連携プラグイン
"""
import os
import threading
import time
import requests
import re
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

try:
    from slack_sdk.web import WebClient
    from slack_sdk.socket_mode import SocketModeClient
    from slack_sdk.socket_mode.response import SocketModeResponse
    from slack_sdk.socket_mode.request import SocketModeRequest
    SLACK_SDK_INSTALLED = True
except ImportError:
    SLACK_SDK_INSTALLED = False

from plugin_manager import BasePlugin
import logger # ★TeloPon標準ロガー

# --- i18n ---
_L = {
    "ja": {
        "plugin_name": "💬 Slack",
        "window_title": "⚙️ Slackコメント連携設定 (リアルタイム版)",
        "err_no_lib": "⚠️ エラー: slack_sdk がインストールされていません。\nコマンドプロンプトで pip install slack_sdk を実行してください。",
        "status_disconnected": "🔌 状態: 切断中",
        "lf_conn": " Slack API 接続設定 ",
        "label_app_token": "App-Level トークン (xapp-...):",
        "label_bot_token": "Bot トークン (xoxb-...):",
        "btn_fetch": "🔄 トークン確認 ＆ チャンネル一覧を取得",
        "fetch_hint": "2つのトークンを入力して「取得」ボタンを押してください",
        "label_channel": "監視するチャンネル:",
        "btn_connect": "接続",
        "lf_ai": " AIへの送信設定 ",
        "label_prompt": "AIに渡す時の指示テキスト (プロンプト):",
        "btn_save": "保存して閉じる",
        "btn_cancel": "キャンセル",
        "status_connected": "⚡ 状態: 接続中 (Socket Mode稼働中)",
        "btn_disconnect": "切断",
        "warn_title": "警告",
        "warn_no_tokens": "両方のトークンと監視するチャンネルを指定してください。",
        "warn_no_bot_token": "Botトークン(xoxb-)を入力してください。\nチャンネル一覧の取得にはBotトークンを使用します。",
        "fetch_loading": "📝 通信中... (ワークスペースのチャンネルを取得しています)",
        "fetch_err": "❌ エラー: ",
        "fetch_network_err": "❌ 通信エラー: ",
        "fetch_success": "✅ 成功: {count}個のチャンネルを取得しました！",
        "fallback_member": "メンバー",
        "default_prompt": "【Slackからのコメント】社内メンバーからのチャットです！コメントを読み上げてリアクションしてください！\n",
    },
    "en": {
        "plugin_name": "💬 Slack",
        "window_title": "⚙️ Slack Comment Integration Settings (Realtime)",
        "err_no_lib": "⚠️ Error: slack_sdk is not installed.\nRun: pip install slack_sdk",
        "status_disconnected": "🔌 Status: Disconnected",
        "lf_conn": " Slack API Connection ",
        "label_app_token": "App-Level Token (xapp-...):",
        "label_bot_token": "Bot Token (xoxb-...):",
        "btn_fetch": "🔄 Verify Tokens & Fetch Channel List",
        "fetch_hint": "Enter both tokens and press the Fetch button",
        "label_channel": "Channel to monitor:",
        "btn_connect": "Connect",
        "lf_ai": " AI Send Settings ",
        "label_prompt": "Instruction text to pass to AI (prompt):",
        "btn_save": "Save & Close",
        "btn_cancel": "Cancel",
        "status_connected": "⚡ Status: Connected (Socket Mode running)",
        "btn_disconnect": "Disconnect",
        "warn_title": "Warning",
        "warn_no_tokens": "Please provide both tokens and the channel to monitor.",
        "warn_no_bot_token": "Please enter the Bot token (xoxb-).\nBot token is used to fetch the channel list.",
        "fetch_loading": "📝 Connecting... (fetching workspace channels)",
        "fetch_err": "❌ Error: ",
        "fetch_network_err": "❌ Network error: ",
        "fetch_success": "✅ Success: Retrieved {count} channels!",
        "fallback_member": "Member",
        "default_prompt": "[Slack Comment] A message from a team member! Please read the comment and react!\n",
    },
    "ru": {
        "plugin_name": "💬 Slack",
        "window_title": "⚙️ Настройки Slack (реальное время)",
        "err_no_lib": "⚠️ Ошибка: slack_sdk не установлен.\nВыполните: pip install slack_sdk",
        "status_disconnected": "🔌 Статус: Отключено",
        "lf_conn": " Настройки Slack API ",
        "label_app_token": "App-Level Token (xapp-...):",
        "label_bot_token": "Bot Token (xoxb-...):",
        "btn_fetch": "🔄 Проверить токены и получить список каналов",
        "fetch_hint": "Введите оба токена и нажмите «Получить»",
        "label_channel": "Канал для мониторинга:",
        "btn_connect": "Подключить",
        "lf_ai": " Настройки отправки ИИ ",
        "label_prompt": "Текст инструкции для ИИ (промпт):",
        "btn_save": "Сохранить и закрыть",
        "btn_cancel": "Отмена",
        "status_connected": "⚡ Статус: Подключено (Socket Mode)",
        "btn_disconnect": "Отключить",
        "warn_title": "Предупреждение",
        "warn_no_tokens": "Укажите оба токена и канал для мониторинга.",
        "warn_no_bot_token": "Введите Bot токен (xoxb-).\nBot токен используется для получения списка каналов.",
        "fetch_loading": "📝 Подключение... (получение каналов рабочего пространства)",
        "fetch_err": "❌ Ошибка: ",
        "fetch_network_err": "❌ Ошибка сети: ",
        "fetch_success": "✅ Успех: Получено {count} каналов!",
        "fallback_member": "Участник",
        "default_prompt": "[Комментарий Slack] Сообщение от участника команды! Прочитайте комментарий и отреагируйте!\n",
    },
    "ko": {
        "plugin_name": "💬 Slack",
        "window_title": "⚙️ Slack 댓글 연동 설정 (실시간)",
        "err_no_lib": "⚠️ 오류: slack_sdk가 설치되어 있지 않습니다.\n실행하세요: pip install slack_sdk",
        "status_disconnected": "🔌 상태: 연결 끊김",
        "lf_conn": " Slack API 연결 ",
        "label_app_token": "App-Level 토큰 (xapp-...):",
        "label_bot_token": "Bot 토큰 (xoxb-...):",
        "btn_fetch": "🔄 토큰 확인 & 채널 목록 가져오기",
        "fetch_hint": "두 토큰을 입력하고 가져오기 버튼을 누르세요",
        "label_channel": "모니터링할 채널:",
        "btn_connect": "연결",
        "lf_ai": " AI 전송 설정 ",
        "label_prompt": "AI에 전달할 지시 텍스트 (프롬프트):",
        "btn_save": "저장 후 닫기",
        "btn_cancel": "취소",
        "status_connected": "⚡ 상태: 연결됨 (Socket Mode 실행 중)",
        "btn_disconnect": "연결 끊기",
        "warn_title": "경고",
        "warn_no_tokens": "두 토큰과 모니터링할 채널을 지정하세요.",
        "warn_no_bot_token": "Bot 토큰(xoxb-)을 입력하세요.\nBot 토큰은 채널 목록을 가져오는 데 사용됩니다.",
        "fetch_loading": "📝 연결 중... (워크스페이스 채널 가져오는 중)",
        "fetch_err": "❌ 오류: ",
        "fetch_network_err": "❌ 네트워크 오류: ",
        "fetch_success": "✅ 성공: {count}개의 채널을 가져왔습니다!",
        "fallback_member": "멤버",
        "default_prompt": "[Slack 댓글] 팀 멤버의 메시지입니다! 댓글을 읽고 리액션 해주세요!\n",
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

class SlackIntegrationPlugin(BasePlugin):
    PLUGIN_ID = "slack_integration"
    PLUGIN_NAME = "Slackコメント連携"
    PLUGIN_VERSION = "1.00"
    PLUGIN_TYPE = "TOOL"

    def get_display_name(self):
        return _t("plugin_name")

    def __init__(self):
        super().__init__()
        self.plugin_queue = None
        self.is_running = False
        self.is_connected = False # UI・システム連動の接続フラグ

        # Slack通信用の変数
        self.loop_thread = None
        self.slack_client = None
        self.user_name_cache = {} # 発言者の名前を記憶しておく辞書
        self._avatar_cache = {}   # 発言者のアバターURLキャッシュ

        self.channel_map = {}

    def get_default_settings(self):
        return {
            "enabled": False,           # ON/OFFフラグ（接続状態）
            "slack_app_token": "",      # xapp- から始まるトークン (WebSocket用)
            "slack_bot_token": "",      # xoxb- から始まるトークン (API用)
            "channel_id": "",           # 監視するチャンネルID
            "channel_name": "",         # 監視するチャンネルの表示名
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
        self.panel.geometry("480x600")
        self.panel.attributes("-topmost", True)

        if not SLACK_SDK_INSTALLED:
            lbl_err = tk.Label(self.panel, text=_t("err_no_lib"), fg="red", bg="#ffe6e6", pady=10)
            lbl_err.pack(fill=tk.X)

        settings = self.get_settings()
        self.is_connected = settings.get("enabled", False)

        main_f = ttk.Frame(self.panel, padding=15)
        main_f.pack(fill=tk.BOTH, expand=True)

        self.lbl_top_status = ttk.Label(main_f, text=_t("status_disconnected"), font=("", 11, "bold"), foreground="gray")
        self.lbl_top_status.pack(anchor="w", pady=(0, 15))

        # --- Slack API 接続設定 ---
        lf_conn = ttk.LabelFrame(main_f, text=_t("lf_conn"), padding=10)
        lf_conn.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(lf_conn, text=_t("label_app_token")).pack(anchor="w")
        self.ent_app_token = ttk.Entry(lf_conn, show="*")
        self.ent_app_token.pack(fill=tk.X, pady=(0, 10))
        self.ent_app_token.insert(0, settings.get("slack_app_token", ""))

        ttk.Label(lf_conn, text=_t("label_bot_token")).pack(anchor="w")
        self.ent_bot_token = ttk.Entry(lf_conn, show="*")
        self.ent_bot_token.pack(fill=tk.X, pady=(0, 10))
        self.ent_bot_token.insert(0, settings.get("slack_bot_token", ""))

        self.btn_fetch = tk.Button(lf_conn, text=_t("btn_fetch"), bg="#4A154B", fg="white", font=("", 9, "bold"), command=self._fetch_channels)
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
        if not hasattr(self, 'btn_connect') or not self.btn_connect.winfo_exists(): return

        if self.is_connected:
            self.lbl_top_status.config(text=_t("status_connected"), foreground="#28a745")
            self.btn_connect.config(text=_t("btn_disconnect"), bg="#dc3545")
            self.ent_app_token.config(state="readonly")
            self.ent_bot_token.config(state="readonly")
            self.cmb_channel.config(state="disabled")
            self.btn_fetch.config(state="disabled")
        else:
            self.lbl_top_status.config(text=_t("status_disconnected"), foreground="gray")
            self.btn_connect.config(text=_t("btn_connect"), bg="#007bff")
            self.ent_app_token.config(state="normal")
            self.ent_bot_token.config(state="normal")
            self.cmb_channel.config(state="readonly")
            self.btn_fetch.config(state="normal")

    def _toggle_connection(self):
        if self.is_connected:
            self.is_connected = False
            self._update_ui_state()
            self._save_settings_from_ui()
            self._stop_bot()
        else:
            app_token = self.ent_app_token.get().strip()
            bot_token = self.ent_bot_token.get().strip()
            raw_channel = self.cmb_channel.get().strip()

            if not app_token or not bot_token or not raw_channel:
                messagebox.showwarning(_t("warn_title"), _t("warn_no_tokens"))
                return

            self.is_connected = True
            self._update_ui_state()
            self._save_settings_from_ui()
            self._start_bot()

    def _fetch_channels(self):
        bot_token = self.ent_bot_token.get().strip()
        if not bot_token:
            messagebox.showwarning(_t("warn_title"), _t("warn_no_bot_token"))
            return

        self.lbl_test_result.config(text=_t("fetch_loading"), foreground="blue")
        self.btn_fetch.config(state="disabled")
        self.panel.update()

        def fetch_task():
            headers = {"Authorization": f"Bearer {bot_token}"}
            try:
                # publicとprivate(鍵付き)の両方を取得
                params = {"types": "public_channel,private_channel", "exclude_archived": "true"}
                res = requests.get("https://slack.com/api/conversations.list", headers=headers, params=params, timeout=5).json()

                if not res.get("ok"):
                    error_msg = res.get("error", "Unknown error")
                    self.panel.after(0, lambda: self._fetch_done(_t("fetch_err") + error_msg, None, None))
                    return

                channels = res.get("channels", [])
                channels_list = []
                temp_map = {}

                for ch in channels:
                    ch_name = ch["name"]
                    ch_id = ch["id"]
                    is_private = ch.get("is_private", False)

                    icon = "🔒" if is_private else "💬"
                    display_name = f"{icon} #{ch_name}"

                    while display_name in temp_map:
                        display_name += " "

                    channels_list.append(display_name)
                    temp_map[display_name] = ch_id

                self.panel.after(0, lambda: self._fetch_done(_t("fetch_success", count=len(channels_list)), channels_list, temp_map))
            except Exception as e:
                self.panel.after(0, lambda: self._fetch_done(_t("fetch_network_err") + str(e)[:30], None, None))

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
        settings["slack_app_token"] = self.ent_app_token.get().strip()
        settings["slack_bot_token"] = self.ent_bot_token.get().strip()
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
    # 🧠 AI連携 & Bot起動ロジック (Socket Mode)
    # ==========================================
    def start(self, prompt_config, plugin_queue):
        self.plugin_queue = plugin_queue
        if self.is_connected:
            self._start_bot()

    def stop(self):
        self.plugin_queue = None

    def _start_bot(self):
        if not SLACK_SDK_INSTALLED:
            logger.error(f"[{self.PLUGIN_NAME}] ❌ slack_sdk がインストールされていません。")
            return

        self.is_running = True
        if self.loop_thread is not None and self.loop_thread.is_alive():
            return

        self.loop_thread = threading.Thread(target=self._run_slack_bot, daemon=True)
        self.loop_thread.start()
        logger.info(f"[{self.PLUGIN_NAME}] ▶️ Slack Socket Mode通信を開始します...")

    def _stop_bot(self):
        self.is_running = False
        if self.slack_client:
            try:
                self.slack_client.disconnect()
            except: pass
        logger.info(f"[{self.PLUGIN_NAME}] ⏹️ Slack連携を停止しました。")

    def _get_user_info(self, user_id, web_client):
        """SlackのユーザーID (U...) から表示名とアバターURLを取得する。
        戻り値: (name, avatar_url)"""
        if user_id in self.user_name_cache:
            name = self.user_name_cache[user_id]
            avatar = self._avatar_cache.get(user_id, "")
            return name, avatar
        try:
            res = web_client.users_info(user=user_id)
            if res["ok"]:
                profile = res["user"]["profile"]
                name = profile.get("display_name") or profile.get("real_name") or _t("fallback_member")
                avatar = profile.get("image_192", "") or profile.get("image_72", "")
                self.user_name_cache[user_id] = name
                self._avatar_cache[user_id] = avatar
                if avatar:
                    logger.debug(f"[Avatar] Slack取得: {name} → {avatar[:40]}")
                return name, avatar
        except Exception as e:
            logger.debug(f"Slack ユーザー情報取得エラー: {e}")
        return _t("fallback_member"), ""

    def _run_slack_bot(self):
        settings = self.get_settings()
        app_token = settings.get("slack_app_token", "").strip()
        bot_token = settings.get("slack_bot_token", "").strip()
        channel_id_str = settings.get("channel_id", "").strip()
        prompt_prefix = settings.get("prompt_text", _t("default_prompt"))

        if not app_token or not bot_token or not channel_id_str:
            logger.warning(f"[{self.PLUGIN_NAME}] ⚠️ トークンまたはチャンネルIDが未設定のため、起動をスキップしました。")
            return

        try:
            # WebClient (API用) と SocketModeClient (リアルタイム受信用) を初期化
            web_client = WebClient(token=bot_token)
            self.slack_client = SocketModeClient(app_token=app_token, web_client=web_client)

            # メッセージを受信した時の処理
            def process(client: SocketModeClient, req: SocketModeRequest):
                if req.type == "events_api":
                    # まず「受け取ったよ」という返事をSlackサーバーに返す(必須ルール)
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    client.send_socket_mode_response(response)

                    # 中身を取り出す
                    event = req.payload.get("event", {})

                    # 普通のテキストメッセージで、かつBot自身の発言ではない場合
                    if event.get("type") == "message" and not event.get("bot_id") and not event.get("subtype"):

                        # 監視対象のチャンネルかチェック
                        if event.get("channel") == channel_id_str:
                            text = event.get("text", "").strip()
                            if not text: return

                            # 発言者の名前とアバターを取得
                            user_id = event.get("user")
                            user_name, avatar_url = self._get_user_info(user_id, web_client)

                            # アバターをCoreに送信
                            if avatar_url and self.plugin_queue:
                                self.send_avatar_map(self.plugin_queue, {user_name: avatar_url})

                            # AIに送るテキストを組み立てる
                            final_text = f"[COMMENT] {user_name}: {text}\n\n{prompt_prefix}"

                            if self.plugin_queue:
                                self.send_text(self.plugin_queue, final_text)
                                logger.info(f"[{self.PLUGIN_NAME}] ⚡ リアルタイム受信: {user_name}のコメントをAIに即時送信しました！")
                            else:
                                logger.debug(f"[{self.PLUGIN_NAME}] メッセージを受信しましたが、TeloPonが待機中のためスキップしました。")

            # イベントリスナーを登録して接続
            self.slack_client.socket_mode_request_listeners.append(process)
            self.slack_client.connect()
            logger.info(f"[{self.PLUGIN_NAME}] ✅ Slackへのログイン完了 (監視ID: {channel_id_str})")

            # 接続を維持するための無限ループ（停止ボタンが押されるまで）
            while self.is_running:
                time.sleep(1)

        except Exception as e:
            if self.is_running:
                logger.warning(f"[{self.PLUGIN_NAME}] ⚠️ Slack通信エラー: {e}")
            self.is_running = False

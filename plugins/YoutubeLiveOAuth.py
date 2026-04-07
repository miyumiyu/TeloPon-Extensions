"""
YoutubeLiveOAuth v1.00 - YouTube Live OAuth2 Plugin for TeloPon
=============================================================
YouTube Data API v3 + OAuth2 による上位互換 YouTube 連携プラグイン。

機能:
  Phase1: OAuth2認証 / タイトル・サムネイル取得 / コメント読み取り
  Phase2: コメント書き込み / AI自動コメント ([CMD]YT:comment ...)
  Phase3: アンケート作成・締切・集計 ([CMD]YT:poll ...)

必要ライブラリ:
  pip install google-api-python-client google-auth-oauthlib pillow
"""

import os
import re
import io
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import logger

# ==========================================
# 多言語対応
# ==========================================
_L = {
    "ja": {
        "plugin_name": "YouTube OAuth連携",
        "window_title": "YouTube OAuth連携 設定",
        "import_error_title": "ライブラリ不足",
        "import_error_msg": (
            "必要なライブラリがインストールされていません。\n"
            "コマンドプロンプトで以下を実行してください。\n\n"
            "pip install google-api-python-client google-auth-oauthlib pillow"
        ),
        # OAuth2 セクション
        "section_oauth": " OAuth2 認証設定 ",
        "lbl_client_id": "Client ID:",
        "lbl_client_secret": "Client Secret:",
        "btn_auth": "Googleで認証する",
        "btn_auth_running": "認証キャンセル",
        "btn_copy": "コピー",
        "auth_ok": "認証済み",
        "auth_none": "未認証",
        "auth_success": "Google認証に成功しました。",
        "auth_error": "認証エラー: {err}",
        "btn_revoke": "認証解除",
        "revoke_confirm": "認証を解除しますか？トークンを削除します。",
        "revoke_done": "認証を解除しました。",
        # 配信選択 セクション
        "section_stream": " 配信を選択 ",
        "btn_fetch_list": "配信一覧を取得",
        "btn_fetching_list": "取得中...",
        "filter_all": "すべて",
        "filter_active": "配信中",
        "filter_upcoming": "予約済み",
        "btn_connect": "この配信に接続",
        "btn_disconnect": "切断",
        "btn_fetching": "接続中...",
        "status_prompt": "認証後「配信一覧を取得」を押してください",
        "status_need_auth": "先にOAuth2認証を行ってください",
        "status_fetching": "配信一覧を取得しています...",
        "status_no_broadcasts": "配信が見つかりませんでした",
        "status_connected": "接続成功 (ID: {video_id})",
        "status_error": "取得エラー: {err_msg}",
        "status_disconnected": "切断されました",
        "broadcast_active": "[配信中]",
        "broadcast_upcoming": "[予約済み]",
        "broadcast_other": "[{status}]",
        # 配信情報プレビュー
        "section_info": " 選択した配信の情報 ",
        "lbl_title_empty": "タイトル: 未取得",
        "lbl_title": "タイトル: {title}",
        "lbl_desc_empty": "説明文: 未取得",
        "lbl_desc": "説明文: {desc}",
        "lbl_thumb_empty": "[ サムネイル未取得 ]",
        "lbl_thumb_fail": "[ 画像取得失敗 ]",
        # 機能設定
        "section_features": " 機能設定 ",
        "chk_comment": "コメント取得",
        "chk_ai_comment": "コメント書き込み",
        "chk_poll": "アンケート",
        "chk_title": "タイトル変更",
        "chk_viewer": "視聴者可",
        "perm_owner": "権限: オーナー（全機能利用可能）",
        "perm_viewer": "権限: 視聴者（コメント・視聴者数のみ）",
        "perm_checking": "権限を確認中...",
        # URL入力
        "label_url": "YouTube ライブURL:",
        "btn_url_check": "確認",
        # 閉じる
        "btn_close": "閉じる",
        # URL解析
        "url_error_title": "エラー",
        "url_error_msg": "YouTubeのURLから動画IDを抽出できませんでした。",
        # プロンプト
        "prompt_addon": (
            "# 【配信の事前情報】\n"
            "あなたは今、以下のYouTubeライブ配信に参加しています。この情報を踏まえて番組を進行してください。\n"
            "* 配信タイトル: {title}\n"
            "* 配信の説明文: {desc}\n"
        ),
        "prompt_cmd": (
            "\n# 【YouTube操作コマンド】\n"
            "以下のコマンドが使えます。テロップテキストの末尾（[MEMO]の直前）に記述してください。\n"
            "配信者の指示に応じて適切なコマンドを使ってください。\n"
            "\n"
            "## コマンド一覧\n"
            "* コメント書き込み: [CMD]YT:comment コメント内容\n"
            "* アンケート作成: [CMD]YT:poll create 質問文|選択肢1|選択肢2|選択肢3\n"
            "  - 選択肢は2～4個。「|」で区切る。\n"
            "* アンケート締切: [CMD]YT:poll close\n"
            "* 視聴者数取得: [CMD]YT:viewers\n"
            "* 配信タイトル変更: [CMD]YT:title 新しいタイトル\n"
            "\n"
            "## 配信者の発言に対する反応ルール\n"
            "* 「○○ってチャットに書いて」「○○ってコメントして」→ [CMD]YT:comment ○○\n"
            "* 「アンケートして」「投票して」→ 設問と選択肢を考えて [CMD]YT:poll create 質問|A|B|C\n"
            "* 「集計して」「結果教えて」「アンケート締め切って」→ [CMD]YT:poll close\n"
            "* 「今何人？」「視聴者数は？」→ [CMD]YT:viewers\n"
            "* 「タイトル変えて」「タイトルを○○にして」→ [CMD]YT:title 新しいタイトル\n"
            "\n"
            "## 例\n"
            "配信者「好きな色をアンケートして」→\n"
            "[TOPIC]アンケート [MAIN]好きな色は？投票してね！ [CMD]YT:poll create 好きな色は？|赤|青|緑\n"
        ),
        "prompt_cmd_limited": (
            "\n# 【YouTube操作コマンド（制限モード）】\n"
            "以下のコマンドが使えます。テロップテキストの末尾（[MEMO]の直前）に記述してください。\n"
            "* コメント書き込み: [CMD]YT:comment コメント内容\n"
            "* 視聴者数取得: [CMD]YT:viewers\n"
            "\n"
            "## 配信者の発言に対する反応ルール\n"
            "* 「○○ってコメントして」→ [CMD]YT:comment ○○\n"
            "* 「今何人？」「視聴者数は？」→ [CMD]YT:viewers\n"
        ),
        "thumb_cue": (
            "【番組ディレクターからのカンペ】\n"
            "今モニターに映したのが本日の配信のサムネイル画像です！"
            "これを見て軽くツッコミや感想を言ってください！"
        ),
        "poll_created": "アンケートを作成しました: {question}",
        "poll_create_error": "アンケート作成エラー: {err}",
        "poll_closed": "アンケートを締め切りました。",
        "poll_result_header": "【アンケート結果】{question}\n",
        "poll_result_line": "  {option}: {count}票",
        "poll_result_cue": (
            "【番組ディレクターからのカンペ】\n"
            "アンケートの結果が出ました！以下の結果を視聴者に発表してください。\n{results}"
        ),
        "poll_close_error": "アンケート締切エラー: {err}",
        "poll_no_active": "現在アクティブなアンケートはありません。",
        "comment_sent": "コメントを送信しました: {text}",
        "comment_error": "コメント送信エラー: {err}",
        "title_changed": "配信タイトルを変更しました: {title}",
        "title_error": "タイトル変更エラー: {err}",
        "viewers_cue": (
            "【番組ディレクターからのカンペ】\n"
            "現在の同時視聴者数は {count} 人です。配信者に教えてあげてください。"
        ),
        "viewers_error": "視聴者数取得エラー: {err}",
        "viewers_unavailable": (
            "【番組ディレクターからのカンペ】\n"
            "現在の視聴者数は取得できませんでした。配信がライブ中でない可能性があります。"
        ),
    },
    "en": {
        "plugin_name": "YouTube OAuth Plugin",
        "window_title": "YouTube OAuth Settings",
        "import_error_title": "Missing Libraries",
        "import_error_msg": (
            "Required libraries are not installed.\n"
            "Please run the following:\n\n"
            "pip install google-api-python-client google-auth-oauthlib pillow"
        ),
        "section_oauth": " OAuth2 Authentication ",
        "lbl_client_id": "Client ID:",
        "lbl_client_secret": "Client Secret:",
        "btn_auth": "Sign in with Google",
        "btn_auth_running": "Cancel auth",
        "btn_copy": "Copy",
        "auth_ok": "Authenticated",
        "auth_none": "Not authenticated",
        "auth_success": "Google authentication successful.",
        "auth_error": "Auth error: {err}",
        "btn_revoke": "Revoke auth",
        "revoke_confirm": "Revoke authentication? Token will be deleted.",
        "revoke_done": "Authentication revoked.",
        "section_stream": " Select Broadcast ",
        "btn_fetch_list": "Fetch broadcast list",
        "btn_fetching_list": "Fetching...",
        "filter_all": "All",
        "filter_active": "Live",
        "filter_upcoming": "Upcoming",
        "btn_connect": "Connect to this broadcast",
        "btn_disconnect": "Disconnect",
        "btn_fetching": "Connecting...",
        "status_prompt": "Press 'Fetch broadcast list' after authentication",
        "status_need_auth": "Please authenticate with OAuth2 first",
        "status_fetching": "Fetching broadcast list...",
        "status_no_broadcasts": "No broadcasts found",
        "status_connected": "Connected (ID: {video_id})",
        "status_error": "Fetch error: {err_msg}",
        "status_disconnected": "Disconnected",
        "broadcast_active": "[Live]",
        "broadcast_upcoming": "[Upcoming]",
        "broadcast_other": "[{status}]",
        "section_info": " Selected Broadcast Info ",
        "lbl_title_empty": "Title: N/A",
        "lbl_title": "Title: {title}",
        "lbl_desc_empty": "Description: N/A",
        "lbl_desc": "Description: {desc}",
        "lbl_thumb_empty": "[ No thumbnail ]",
        "lbl_thumb_fail": "[ Image failed ]",
        "section_features": " Features ",
        "chk_comment": "Fetch comments",
        "chk_ai_comment": "Write comments",
        "chk_poll": "Polls",
        "chk_title": "Change title",
        "chk_viewer": "Viewer",
        "perm_owner": "Permission: Owner (all features available)",
        "perm_viewer": "Permission: Viewer (comment & viewers only)",
        "perm_checking": "Checking permissions...",
        "label_url": "YouTube Live URL:",
        "btn_url_check": "Check",
        "btn_close": "Close",
        "url_error_title": "Error",
        "url_error_msg": "Could not extract a video ID from the YouTube URL.",
        "prompt_addon": (
            "# [Broadcast Info]\n"
            "You are currently participating in the following YouTube live stream. "
            "Please host the show based on this information.\n"
            "* Stream title: {title}\n"
            "* Stream description: {desc}\n"
        ),
        "prompt_cmd": (
            "\n# [YouTube Commands]\n"
            "You can use the following commands. Place them at the end of telop text (before [MEMO]).\n"
            "* Write comment: [CMD]YT:comment Your comment here\n"
            "* Create poll: [CMD]YT:poll create Question?|Option1|Option2|Option3\n"
            "  - 2-4 options, separated by '|'.\n"
            "* Close poll: [CMD]YT:poll close\n"
            "  - Results will be fed back to the streamer.\n"
            "* Get viewer count: [CMD]YT:viewers\n"
            "* Change stream title: [CMD]YT:title New Title Here\n"
            "\nExample: If the streamer says 'create a poll about favorite colors':\n"
            "[TOPIC]Poll [MAIN]What's your favorite color? [CMD]YT:poll create What's your favorite color?|Red|Blue|Green\n"
        ),
        "prompt_cmd_limited": (
            "\n# [YouTube Commands (Limited)]\n"
            "* Write comment: [CMD]YT:comment Your comment here\n"
            "* Get viewer count: [CMD]YT:viewers\n"
        ),
        "thumb_cue": (
            "[Cue from Director]\n"
            "The image now shown on the monitor is today's stream thumbnail! "
            "Please react to it with a quick comment or impression!"
        ),
        "poll_created": "Poll created: {question}",
        "poll_create_error": "Poll creation error: {err}",
        "poll_closed": "Poll closed.",
        "poll_result_header": "[Poll Results] {question}\n",
        "poll_result_line": "  {option}: {count} votes",
        "poll_result_cue": (
            "[Cue from Director]\n"
            "The poll results are in! Please announce the following to viewers.\n{results}"
        ),
        "poll_close_error": "Poll close error: {err}",
        "poll_no_active": "No active poll found.",
        "comment_sent": "Comment sent: {text}",
        "comment_error": "Comment error: {err}",
        "title_changed": "Stream title changed: {title}",
        "title_error": "Title change error: {err}",
        "viewers_cue": (
            "[Cue from Director]\n"
            "The current concurrent viewer count is {count}. Please tell the streamer."
        ),
        "viewers_error": "Viewer count error: {err}",
        "viewers_unavailable": (
            "[Cue from Director]\n"
            "Could not retrieve viewer count. The stream may not be live."
        ),
    },
    "ko": {
        "plugin_name": "YouTube OAuth 연동",
        "window_title": "YouTube OAuth 설정",
        "import_error_title": "라이브러리 부족",
        "import_error_msg": (
            "필요한 라이브러리가 설치되지 않았습니다.\n"
            "다음 명령을 실행하세요:\n\n"
            "pip install google-api-python-client google-auth-oauthlib pillow"
        ),
        "section_oauth": " OAuth2 인증 설정 ",
        "lbl_client_id": "Client ID:",
        "lbl_client_secret": "Client Secret:",
        "btn_auth": "Google로 인증",
        "btn_auth_running": "인증 취소",
        "btn_copy": "복사",
        "auth_ok": "인증 완료",
        "auth_none": "미인증",
        "auth_success": "Google 인증에 성공했습니다.",
        "auth_error": "인증 오류: {err}",
        "btn_revoke": "인증 해제",
        "revoke_confirm": "인증을 해제하시겠습니까? 토큰이 삭제됩니다.",
        "revoke_done": "인증이 해제되었습니다.",
        "section_stream": " 방송 선택 ",
        "btn_fetch_list": "방송 목록 가져오기",
        "btn_fetching_list": "가져오는 중...",
        "filter_all": "전체",
        "filter_active": "방송중",
        "filter_upcoming": "예약됨",
        "btn_connect": "이 방송에 연결",
        "btn_disconnect": "연결 끊기",
        "btn_fetching": "연결 중...",
        "status_prompt": "인증 후 '방송 목록 가져오기'를 누르세요",
        "status_need_auth": "먼저 OAuth2 인증을 해주세요",
        "status_fetching": "방송 목록 가져오는 중...",
        "status_no_broadcasts": "방송을 찾을 수 없습니다",
        "status_connected": "연결됨 (ID: {video_id})",
        "status_error": "오류: {err_msg}",
        "status_disconnected": "연결 끊김",
        "broadcast_active": "[방송중]",
        "broadcast_upcoming": "[예약됨]",
        "broadcast_other": "[{status}]",
        "section_info": " 선택한 방송 정보 ",
        "lbl_title_empty": "제목: 없음",
        "lbl_title": "제목: {title}",
        "lbl_desc_empty": "설명: 없음",
        "lbl_desc": "설명: {desc}",
        "lbl_thumb_empty": "[ 썸네일 없음 ]",
        "lbl_thumb_fail": "[ 이미지 로드 실패 ]",
        "section_features": " 기능 설정 ",
        "chk_comment": "댓글 가져오기",
        "chk_ai_comment": "댓글 작성",
        "chk_poll": "설문",
        "chk_title": "제목 변경",
        "chk_viewer": "시청자",
        "perm_owner": "권한: 소유자 (전체 기능 사용 가능)",
        "perm_viewer": "권한: 시청자 (댓글·시청자 수만)",
        "perm_checking": "권한 확인 중...",
        "label_url": "YouTube 라이브 URL:",
        "btn_url_check": "확인",
        "btn_close": "닫기",
        "url_error_title": "오류",
        "url_error_msg": "YouTube URL에서 동영상 ID를 추출할 수 없습니다.",
        "prompt_addon": (
            "# [Broadcast Info]\n"
            "You are currently participating in the following YouTube live stream. "
            "Please host the show based on this information.\n"
            "* Stream title: {title}\n"
            "* Stream description: {desc}\n"
        ),
        "prompt_cmd": (
            "\n# [YouTube Commands]\n"
            "You can use the following commands. Place them at the end of telop text (before [MEMO]).\n"
            "* Write comment: [CMD]YT:comment Your comment here\n"
            "* Create poll: [CMD]YT:poll create Question?|Option1|Option2|Option3\n"
            "  - 2-4 options, separated by '|'.\n"
            "* Close poll: [CMD]YT:poll close\n"
            "  - Results will be fed back to the streamer.\n"
            "* Get viewer count: [CMD]YT:viewers\n"
            "* Change stream title: [CMD]YT:title New Title Here\n"
        ),
        "prompt_cmd_limited": (
            "\n# [YouTube Commands (Limited)]\n"
            "* Write comment: [CMD]YT:comment Your comment here\n"
            "* Get viewer count: [CMD]YT:viewers\n"
        ),
        "thumb_cue": (
            "[Cue from Director]\n"
            "The image now shown on the monitor is today's stream thumbnail! "
            "Please react to it with a quick comment or impression!"
        ),
        "poll_created": "설문 생성됨: {question}",
        "poll_create_error": "설문 생성 오류: {err}",
        "poll_closed": "설문이 마감되었습니다.",
        "poll_result_header": "[설문 결과] {question}\n",
        "poll_result_line": "  {option}: {count}표",
        "poll_result_cue": (
            "[Cue from Director]\n"
            "The poll results are in! Please announce the following to viewers.\n{results}"
        ),
        "poll_close_error": "설문 마감 오류: {err}",
        "poll_no_active": "현재 활성 설문이 없습니다.",
        "comment_sent": "댓글 전송됨: {text}",
        "comment_error": "댓글 전송 오류: {err}",
        "title_changed": "방송 제목 변경됨: {title}",
        "title_error": "제목 변경 오류: {err}",
        "viewers_cue": (
            "[Cue from Director]\n"
            "The current concurrent viewer count is {count}. Please tell the streamer."
        ),
        "viewers_error": "시청자 수 오류: {err}",
        "viewers_unavailable": (
            "[Cue from Director]\n"
            "Could not retrieve viewer count. The stream may not be live."
        ),
    },
    "ru": {
        "plugin_name": "YouTube OAuth",
        "window_title": "Настройки YouTube OAuth",
        "import_error_title": "Отсутствуют библиотеки",
        "import_error_msg": (
            "Необходимые библиотеки не установлены.\n"
            "Выполните:\n\n"
            "pip install google-api-python-client google-auth-oauthlib pillow"
        ),
        "section_oauth": " Аутентификация OAuth2 ",
        "lbl_client_id": "Client ID:",
        "lbl_client_secret": "Client Secret:",
        "btn_auth": "Войти через Google",
        "btn_auth_running": "Отмена",
        "btn_copy": "Копировать",
        "auth_ok": "Аутентифицирован",
        "auth_none": "Не аутентифицирован",
        "auth_success": "Аутентификация Google прошла успешно.",
        "auth_error": "Ошибка аутентификации: {err}",
        "btn_revoke": "Отозвать авторизацию",
        "revoke_confirm": "Отозвать аутентификацию? Токен будет удалён.",
        "revoke_done": "Аутентификация отозвана.",
        "section_stream": " Выбор трансляции ",
        "btn_fetch_list": "Получить список",
        "btn_fetching_list": "Загрузка...",
        "filter_all": "Все",
        "filter_active": "В эфире",
        "filter_upcoming": "Запланировано",
        "btn_connect": "Подключить к трансляции",
        "btn_disconnect": "Отключить",
        "btn_fetching": "Подключение...",
        "status_prompt": "Нажмите «Получить список» после аутентификации",
        "status_need_auth": "Сначала пройдите OAuth2 аутентификацию",
        "status_fetching": "Получение списка...",
        "status_no_broadcasts": "Трансляции не найдены",
        "status_connected": "Подключено (ID: {video_id})",
        "status_error": "Ошибка: {err_msg}",
        "status_disconnected": "Отключено",
        "broadcast_active": "[В эфире]",
        "broadcast_upcoming": "[Запланировано]",
        "broadcast_other": "[{status}]",
        "section_info": " Информация о трансляции ",
        "lbl_title_empty": "Заголовок: Н/Д",
        "lbl_title": "Заголовок: {title}",
        "lbl_desc_empty": "Описание: Н/Д",
        "lbl_desc": "Описание: {desc}",
        "lbl_thumb_empty": "[ Нет миниатюры ]",
        "lbl_thumb_fail": "[ Не удалось загрузить ]",
        "section_features": " Функции ",
        "chk_comment": "Получение комментариев",
        "chk_ai_comment": "Запись комментариев",
        "chk_poll": "Опросы",
        "chk_title": "Изменение заголовка",
        "chk_viewer": "Зритель",
        "perm_owner": "Права: Владелец (все функции доступны)",
        "perm_viewer": "Права: Зритель (только комментарии и зрители)",
        "perm_checking": "Проверка прав...",
        "label_url": "YouTube Live URL:",
        "btn_url_check": "Проверить",
        "btn_close": "Закрыть",
        "url_error_title": "Ошибка",
        "url_error_msg": "Не удалось извлечь ID видео из YouTube URL.",
        "prompt_addon": (
            "# [Broadcast Info]\n"
            "You are currently participating in the following YouTube live stream. "
            "Please host the show based on this information.\n"
            "* Stream title: {title}\n"
            "* Stream description: {desc}\n"
        ),
        "prompt_cmd": (
            "\n# [YouTube Commands]\n"
            "You can use the following commands. Place them at the end of telop text (before [MEMO]).\n"
            "* Write comment: [CMD]YT:comment Your comment here\n"
            "* Create poll: [CMD]YT:poll create Question?|Option1|Option2|Option3\n"
            "  - 2-4 options, separated by '|'.\n"
            "* Close poll: [CMD]YT:poll close\n"
            "  - Results will be fed back to the streamer.\n"
            "* Get viewer count: [CMD]YT:viewers\n"
            "* Change stream title: [CMD]YT:title New Title Here\n"
        ),
        "prompt_cmd_limited": (
            "\n# [YouTube Commands (Limited)]\n"
            "* Write comment: [CMD]YT:comment Your comment here\n"
            "* Get viewer count: [CMD]YT:viewers\n"
        ),
        "thumb_cue": (
            "[Cue from Director]\n"
            "The image now shown on the monitor is today's stream thumbnail! "
            "Please react to it with a quick comment or impression!"
        ),
        "poll_created": "Опрос создан: {question}",
        "poll_create_error": "Ошибка создания опроса: {err}",
        "poll_closed": "Опрос закрыт.",
        "poll_result_header": "[Результаты опроса] {question}\n",
        "poll_result_line": "  {option}: {count} голосов",
        "poll_result_cue": (
            "[Cue from Director]\n"
            "The poll results are in! Please announce the following to viewers.\n{results}"
        ),
        "poll_close_error": "Ошибка закрытия опроса: {err}",
        "poll_no_active": "Нет активного опроса.",
        "comment_sent": "Комментарий отправлен: {text}",
        "comment_error": "Ошибка комментария: {err}",
        "title_changed": "Заголовок изменён: {title}",
        "title_error": "Ошибка изменения заголовка: {err}",
        "viewers_cue": (
            "[Cue from Director]\n"
            "The current concurrent viewer count is {count}. Please tell the streamer."
        ),
        "viewers_error": "Ошибка получения зрителей: {err}",
        "viewers_unavailable": (
            "[Cue from Director]\n"
            "Could not retrieve viewer count. The stream may not be live."
        ),
    },
}


def _t(key: str, **kwargs) -> str:
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
# ライブラリ読み込み
# ==========================================
_HAS_DEPS = True
try:
    from googleapiclient.discovery import build as gapi_build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GAuthRequest
    from PIL import Image, ImageTk
    import requests
except ImportError:
    _HAS_DEPS = False

from plugin_manager import BasePlugin

# OAuth2 スコープ (YouTube全操作)
_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# トークン保存パス
_TOKEN_PATH = os.path.join("plugins", "youtube_oauth_token.json")


class YoutubeLiveOAuth(BasePlugin):
    PLUGIN_ID = "youtube_live_oauth"
    PLUGIN_NAME = "YouTube OAuth連携"
    PLUGIN_TYPE = "TOOL"

    # CMD ハイブリッド: [CMD]YT:xxx
    IDENTIFIER = "YT"

    def __init__(self):
        super().__init__()
        self.plugin_queue = None
        self.is_running = False
        self.chat_thread = None
        self.thumb_thread = None
        self._live_queue = None
        self._live_prompt_config = None

        # OAuth2
        self._credentials = None
        self._youtube = None  # googleapiclient service

        # 配信情報
        self.video_id = None
        self.live_chat_id = None
        self.yt_title = ""
        self.yt_desc = ""
        self.thumbnail_bytes = None
        self.is_connected = False

        # 権限
        self._is_owner = False

        # アンケート
        self._active_poll_id = None
        self._active_poll_question = ""

        # コメント取得用の pageToken
        self._chat_page_token = None

        # 認証ユーザー情報
        self._auth_user_name = ""
        self._auth_user_thumb_url = ""
        self._auth_user_photo = None  # ImageTk.PhotoImage 参照保持用

        # UI
        self.preview_photo = None

        # 起動時にトークン読み込み
        self._load_token()

    def get_display_name(self) -> str:
        return _t("plugin_name")

    def get_default_settings(self):
        return {
            "enabled": False,
            "saved_url": "",
            "client_id": "",
            "client_secret": "",
            "fetch_comments": True,
            "ai_comment": True,
            "ai_poll": True,
            "ai_title": True,
            "viewer_comment": True,
            "viewer_poll": True,
            "viewer_title": True,
        }

    # ==========================================
    # OAuth2 トークン管理
    # ==========================================
    def _build_youtube_service(self):
        """スレッドセーフな YouTube API サービスを新規作成する。
        httplib2 はスレッドセーフでないため、スレッドごとに新しいインスタンスが必要。"""
        if not self._credentials:
            return None
        if self._credentials.expired and self._credentials.refresh_token:
            self._credentials.refresh(GAuthRequest())
            self._save_token()
        return gapi_build("youtube", "v3", credentials=self._credentials)

    def _load_token(self):
        """保存済みトークンを読み込む"""
        if not _HAS_DEPS:
            return
        if os.path.exists(_TOKEN_PATH):
            try:
                self._credentials = Credentials.from_authorized_user_file(_TOKEN_PATH, _SCOPES)
                if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                    self._credentials.refresh(GAuthRequest())
                    self._save_token()
                if self._credentials and self._credentials.valid:
                    self._youtube = self._build_youtube_service()
                    self._fetch_auth_user_info()
                    logger.info(f"[{self.PLUGIN_NAME}] OAuth2トークンを読み込みました。")
                else:
                    self._credentials = None
            except Exception as e:
                logger.warning(f"[{self.PLUGIN_NAME}] トークン読み込みエラー: {e}")
                self._credentials = None

    def _fetch_auth_user_info(self):
        """認証ユーザーのチャンネル名とサムネイルを取得"""
        if not self._youtube:
            return
        try:
            resp = self._youtube.channels().list(part="snippet", mine=True).execute()
            items = resp.get("items", [])
            if items:
                snippet = items[0].get("snippet", {})
                self._auth_user_name = snippet.get("title", "")
                thumbs = snippet.get("thumbnails", {})
                for q in ("default", "medium", "high"):
                    if q in thumbs:
                        self._auth_user_thumb_url = thumbs[q]["url"]
                        break
                logger.info(f"[{self.PLUGIN_NAME}] 認証ユーザー: {self._auth_user_name}")
        except Exception as e:
            logger.debug(f"[{self.PLUGIN_NAME}] ユーザー情報取得エラー: {e}")

    def _save_token(self):
        """トークンをファイルに保存"""
        if self._credentials:
            try:
                with open(_TOKEN_PATH, "w", encoding="utf-8") as f:
                    f.write(self._credentials.to_json())
            except Exception as e:
                logger.error(f"[{self.PLUGIN_NAME}] トークン保存エラー: {e}")

    def _run_oauth_flow(self, client_id, client_secret):
        """OAuth2認証フローを実行（ブラウザが開く）"""
        import webbrowser

        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, _SCOPES)

        # 認証URLを取得してUI表示
        auth_url, _ = flow.authorization_url(prompt="consent")
        if hasattr(self, 'panel') and self.panel.winfo_exists():
            self.panel.after(0, lambda: self._show_auth_url(auth_url))

        # ブラウザを開いてローカルサーバーで待機
        # SO_REUSEADDR でポート再利用可能にする（キャンセル後の再認証でポート競合を防止）
        import wsgiref.simple_server
        original_init = wsgiref.simple_server.WSGIServer.__init__

        def _patched_init(self_server, *args, **kwargs):
            import socket
            self_server.allow_reuse_address = True
            original_init(self_server, *args, **kwargs)
            self_server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        wsgiref.simple_server.WSGIServer.__init__ = _patched_init
        try:
            self._credentials = flow.run_local_server(port=8099, open_browser=True)
        finally:
            wsgiref.simple_server.WSGIServer.__init__ = original_init

        if getattr(self, '_auth_cancelled', False):
            self._credentials = None
            return

        self._save_token()
        self._youtube = self._build_youtube_service()
        self._fetch_auth_user_info()

    def _show_auth_url(self, auth_url):
        """認証URL + コピーボタンを表示"""
        if not hasattr(self, 'lbl_auth_status'):
            return
        parent = self.lbl_auth_status.master
        self._auth_url_f = ttk.Frame(parent)
        self._auth_url_f.pack(fill=tk.X, pady=(2, 0))

        url_entry = ttk.Entry(self._auth_url_f, font=("", 7))
        url_entry.pack(side="left", fill=tk.X, expand=True, padx=(0, 3))
        url_entry.insert(0, auth_url)
        url_entry.config(state="readonly")

        def _copy():
            self.panel.clipboard_clear()
            self.panel.clipboard_append(auth_url)
        tk.Button(self._auth_url_f, text=_t("btn_copy"), font=("", 8),
                  command=_copy).pack(side="right")

    def _hide_auth_url(self):
        """認証URL表示を消す"""
        if hasattr(self, '_auth_url_f') and self._auth_url_f.winfo_exists():
            self._auth_url_f.destroy()

    def _revoke_token(self):
        """トークンを削除"""
        self._credentials = None
        self._youtube = None
        self._auth_user_name = ""
        self._auth_user_thumb_url = ""
        self._auth_user_photo = None
        if os.path.exists(_TOKEN_PATH):
            os.remove(_TOKEN_PATH)

    @property
    def is_authenticated(self):
        return self._credentials is not None and self._credentials.valid

    # ==========================================
    # 設定UI
    # ==========================================
    def open_settings_ui(self, parent_window):
        if not _HAS_DEPS:
            messagebox.showerror(_t("import_error_title"), _t("import_error_msg"))
            return

        self.panel = tk.Toplevel(parent_window)
        self.panel.title(_t("window_title"))
        self.panel.geometry("820x600")
        self.panel.minsize(780, 500)
        self.panel.attributes("-topmost", True)

        settings = self.get_settings()

        # ========== 2列レイアウト ==========
        columns_f = ttk.Frame(self.panel, padding=10)
        columns_f.pack(fill=tk.BOTH, expand=True)

        # --- 左列: 認証 + 配信選択 ---
        left_f = ttk.Frame(columns_f)
        left_f.pack(side="left", fill=tk.BOTH, expand=True, padx=(0, 5))

        # OAuth2 セクション
        oauth_f = ttk.LabelFrame(left_f, text=_t("section_oauth"), padding=8)
        oauth_f.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(oauth_f, text=_t("lbl_client_id")).pack(anchor="w")
        self._var_client_id = tk.StringVar(value=settings.get("client_id", ""))
        self._var_client_id.trace_add("write", self._on_credentials_changed)
        self.ent_client_id = ttk.Entry(oauth_f, font=("", 9), show="*", textvariable=self._var_client_id)
        self.ent_client_id.pack(fill=tk.X, pady=(0, 3))

        ttk.Label(oauth_f, text=_t("lbl_client_secret")).pack(anchor="w")
        self._var_client_secret = tk.StringVar(value=settings.get("client_secret", ""))
        self._var_client_secret.trace_add("write", self._on_credentials_changed)
        self.ent_client_secret = ttk.Entry(oauth_f, font=("", 9), show="*", textvariable=self._var_client_secret)
        self.ent_client_secret.pack(fill=tk.X, pady=(0, 3))

        auth_btn_f = ttk.Frame(oauth_f)
        auth_btn_f.pack(fill=tk.X, pady=(3, 0))
        if self.is_authenticated:
            self.btn_auth = tk.Button(auth_btn_f, text=_t("btn_revoke"), bg="#dc3545", fg="white",
                                      font=("", 9, "bold"), command=self._on_revoke_click)
        else:
            self.btn_auth = tk.Button(auth_btn_f, text=_t("btn_auth"), bg="#4285f4", fg="white",
                                      font=("", 9, "bold"), command=self._on_auth_click)
        self.btn_auth.pack(side="left")
        # 未認証でID/Secretが空ならボタン非アクティブ
        if not self.is_authenticated:
            if not (settings.get("client_id", "") and settings.get("client_secret", "")):
                self.btn_auth.config(state="disabled")

        auth_info_f = ttk.Frame(oauth_f)
        auth_info_f.pack(fill=tk.X, pady=(3, 0))
        self.lbl_auth_thumb = ttk.Label(auth_info_f)
        self.lbl_auth_thumb.pack(side="left", padx=(0, 5))
        self.lbl_auth_status = ttk.Label(
            auth_info_f,
            text=_t("auth_ok") if self.is_authenticated else _t("auth_none"),
            foreground="green" if self.is_authenticated else "gray"
        )
        self.lbl_auth_status.pack(side="left")
        if self.is_authenticated and self._auth_user_name:
            self._show_auth_user_info()

        # 配信選択 セクション
        stream_f = ttk.LabelFrame(left_f, text=_t("section_stream"), padding=8)
        stream_f.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        fetch_f = ttk.Frame(stream_f)
        fetch_f.pack(fill=tk.X, pady=(0, 3))
        self.btn_fetch_list = tk.Button(fetch_f, text=_t("btn_fetch_list"), bg="#007bff", fg="white",
                                        font=("", 9, "bold"), command=self._on_fetch_list_click)
        self.btn_fetch_list.pack(side="left")

        list_f = ttk.Frame(stream_f)
        list_f.pack(fill=tk.BOTH, expand=True, pady=(0, 3))
        list_scroll = ttk.Scrollbar(list_f, orient="vertical")
        self.lst_broadcasts = tk.Listbox(list_f, height=4, font=("", 9),
                                          yscrollcommand=list_scroll.set, exportselection=False)
        list_scroll.config(command=self.lst_broadcasts.yview)
        self.lst_broadcasts.pack(side="left", fill=tk.BOTH, expand=True)
        list_scroll.pack(side="right", fill="y")
        self.lst_broadcasts.bind("<<ListboxSelect>>", self._on_broadcast_select)
        self._broadcast_items = []

        ttk.Label(stream_f, text=_t("label_url"), font=("", 8)).pack(anchor="w")
        url_input_f = ttk.Frame(stream_f)
        url_input_f.pack(fill=tk.X, pady=(0, 3))
        self._var_url = tk.StringVar(value=settings.get("saved_url", ""))
        self._var_url.trace_add("write", self._on_url_changed)
        self.ent_url = ttk.Entry(url_input_f, font=("", 9), textvariable=self._var_url)
        self.ent_url.pack(side="left", fill=tk.X, expand=True, padx=(0, 3))
        self.btn_url_check = tk.Button(url_input_f, text=_t("btn_url_check"), bg="#6c757d", fg="white",
                                        font=("", 8, "bold"), command=self._on_url_check_click, state="disabled")
        self.btn_url_check.pack(side="right")

        self.lbl_status = ttk.Label(stream_f, text=_t("status_prompt"), foreground="gray")
        self.lbl_status.pack(pady=(0, 3))

        btn_f = ttk.Frame(stream_f)
        btn_f.pack(fill=tk.X)
        self.btn_connect = tk.Button(btn_f, text=_t("btn_connect"), bg="#007bff", fg="white",
                                      font=("", 10, "bold"), command=self._on_connect_click, state="disabled")
        self.btn_connect.pack(side="left")
        self.btn_disconnect = tk.Button(btn_f, text=_t("btn_disconnect"), bg="#dc3545", fg="white",
                                         font=("", 10, "bold"), command=self._disconnect)

        # --- 右列: 配信情報 + 機能設定 ---
        right_f = ttk.Frame(columns_f)
        right_f.pack(side="left", fill=tk.BOTH, expand=True, padx=(5, 0))

        # 配信情報プレビュー
        info_f = ttk.LabelFrame(right_f, text=_t("section_info"), padding=8)
        info_f.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.lbl_title = ttk.Label(info_f, text=_t("lbl_title_empty"), font=("", 10, "bold"), wraplength=350)
        self.lbl_title.pack(anchor="w", pady=(0, 3))
        self.lbl_desc = tk.Label(info_f, text=_t("lbl_desc_empty"), justify="left", anchor="nw",
                                 fg="#555", wraplength=350, height=2)
        self.lbl_desc.pack(fill=tk.X, pady=(0, 3))
        self.lbl_preview = ttk.Label(info_f, text=_t("lbl_thumb_empty"), background="#dddddd", anchor="center")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True)
        self.lbl_permission = ttk.Label(info_f, text="", foreground="gray")
        self.lbl_permission.pack(anchor="w", pady=(3, 0))

        # 機能設定（グリッド: 機能 | 視聴者可）
        feat_f = ttk.LabelFrame(right_f, text=_t("section_features"), padding=8)
        feat_f.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(feat_f, text="", width=14).grid(row=0, column=0, sticky="w")
        ttk.Label(feat_f, text=_t("chk_viewer"), font=("", 7), foreground="gray").grid(row=0, column=1)

        self.var_fetch_comments = tk.BooleanVar(value=settings.get("fetch_comments", True))
        self._chk_comment = ttk.Checkbutton(feat_f, text=_t("chk_comment"), variable=self.var_fetch_comments)
        self._chk_comment.grid(row=1, column=0, sticky="w", pady=1)

        self.var_ai_comment = tk.BooleanVar(value=settings.get("ai_comment", True))
        self._chk_ai_comment = ttk.Checkbutton(feat_f, text=_t("chk_ai_comment"), variable=self.var_ai_comment)
        self._chk_ai_comment.grid(row=2, column=0, sticky="w", pady=1)
        self.var_viewer_comment = tk.BooleanVar(value=settings.get("viewer_comment", True))
        self._chk_v_comment = ttk.Checkbutton(feat_f, variable=self.var_viewer_comment)
        self._chk_v_comment.grid(row=2, column=1, pady=1)

        self.var_ai_poll = tk.BooleanVar(value=settings.get("ai_poll", True))
        self._chk_poll = ttk.Checkbutton(feat_f, text=_t("chk_poll"), variable=self.var_ai_poll)
        self._chk_poll.grid(row=3, column=0, sticky="w", pady=1)
        self.var_viewer_poll = tk.BooleanVar(value=settings.get("viewer_poll", False))
        self._chk_v_poll = ttk.Checkbutton(feat_f, variable=self.var_viewer_poll)
        self._chk_v_poll.grid(row=3, column=1, pady=1)

        self.var_ai_title = tk.BooleanVar(value=settings.get("ai_title", True))
        self._chk_title = ttk.Checkbutton(feat_f, text=_t("chk_title"), variable=self.var_ai_title)
        self._chk_title.grid(row=4, column=0, sticky="w", pady=1)
        self.var_viewer_title = tk.BooleanVar(value=settings.get("viewer_title", False))
        self._chk_v_title = ttk.Checkbutton(feat_f, variable=self.var_viewer_title)
        self._chk_v_title.grid(row=4, column=1, pady=1)

        self._owner_only_checks = [self._chk_poll, self._chk_title]
        self._all_feature_checks = [self._chk_comment, self._chk_ai_comment, self._chk_poll, self._chk_title]
        self._all_viewer_checks = [self._chk_v_comment, self._chk_v_poll, self._chk_v_title]

        # 閉じるボタン
        ttk.Button(right_f, text=_t("btn_close"), command=self._on_close_settings).pack(fill=tk.X)

        # 既に接続済みならUI復元
        if self.is_connected and self.video_id:
            self._update_ui_connected()
            self.btn_connect.pack_forget()
            self.btn_disconnect.pack(side="left")

        # ライブ中（接続済み含む）なら機能設定をグレーアウト
        if self.is_running or (self.is_connected and self._live_queue is not None):
            self._set_features_locked(True)

        # URLが既に入っていたら確認ボタンをアクティブに
        if self._var_url.get().strip():
            self.btn_url_check.config(state="normal")

    def _on_close_settings(self):
        """設定画面を閉じる際に設定を保存"""
        settings = self.get_settings()
        settings["client_id"] = self.ent_client_id.get().strip()
        settings["client_secret"] = self.ent_client_secret.get().strip()
        settings["fetch_comments"] = self.var_fetch_comments.get()
        settings["ai_comment"] = self.var_ai_comment.get()
        settings["ai_poll"] = self.var_ai_poll.get()
        settings["ai_title"] = self.var_ai_title.get()
        settings["viewer_comment"] = self.var_viewer_comment.get()
        settings["viewer_poll"] = self.var_viewer_poll.get()
        settings["viewer_title"] = self.var_viewer_title.get()
        self.save_settings(settings)
        self.panel.destroy()

    # ==========================================
    # OAuth2 UI アクション
    # ==========================================
    def _on_credentials_changed(self, *_):
        """Client ID/Secret入力の変更を監視してボタンの有効/無効を切替"""
        if self.is_authenticated:
            return  # 認証済みなら無視
        has_creds = bool(self._var_client_id.get().strip() and self._var_client_secret.get().strip())
        if hasattr(self, 'btn_auth'):
            self.btn_auth.config(state="normal" if has_creds else "disabled")

    def _on_auth_cancel(self):
        """認証中キャンセル"""
        self._auth_cancelled = True
        self._hide_auth_url()
        self.btn_auth.config(state="normal", text=_t("btn_auth"), bg="#4285f4",
                             command=self._on_auth_click)
        self.lbl_auth_status.config(text=_t("auth_none"), foreground="gray")
        logger.info(f"[{self.PLUGIN_NAME}] 認証キャンセル")

    def _on_auth_click(self):
        """認証ボタンクリック"""
        client_id = self.ent_client_id.get().strip()
        client_secret = self.ent_client_secret.get().strip()
        if not client_id or not client_secret:
            return

        # 設定保存
        settings = self.get_settings()
        settings["client_id"] = client_id
        settings["client_secret"] = client_secret
        self.save_settings(settings)

        self._auth_cancelled = False
        self.btn_auth.config(state="normal", text=_t("btn_auth_running"), bg="#dc3545",
                             command=self._on_auth_cancel)

        def _do_auth():
            try:
                self._run_oauth_flow(client_id, client_secret)
                if self._auth_cancelled:
                    return
                if hasattr(self, 'panel') and self.panel.winfo_exists():
                    self.panel.after(0, self._hide_auth_url)
                    self.panel.after(0, lambda: self._update_auth_ui(True))
                logger.info(f"[{self.PLUGIN_NAME}] OAuth2認証成功")
            except Exception as e:
                if self._auth_cancelled:
                    return
                if hasattr(self, 'panel') and self.panel.winfo_exists():
                    self.panel.after(0, self._hide_auth_url)
                    self.panel.after(0, lambda: self._update_auth_ui(False, str(e)))
                logger.error(f"[{self.PLUGIN_NAME}] OAuth2認証エラー: {e}")

        threading.Thread(target=_do_auth, daemon=True).start()

    def _update_auth_ui(self, success, err=None):
        if success:
            self.btn_auth.config(state="normal", text=_t("btn_revoke"), bg="#dc3545",
                                 command=self._on_revoke_click)
            self.lbl_auth_status.config(text=_t("auth_ok"), foreground="green")
            self._show_auth_user_info()
        else:
            self.btn_auth.config(state="normal", text=_t("btn_auth"), bg="#4285f4",
                                 command=self._on_auth_click)
            self.lbl_auth_status.config(
                text=_t("auth_error", err=err or "unknown"), foreground="red"
            )

    def _show_auth_user_info(self):
        """認証ユーザーのサムネイルと名前をUIに表示"""
        if not self._auth_user_name:
            return
        # ステータスラベルに名前を追加
        self.lbl_auth_status.config(
            text=f"{_t('auth_ok')}  {self._auth_user_name}",
            foreground="green"
        )
        # サムネイル取得（バックグラウンド）
        if self._auth_user_thumb_url:
            threading.Thread(
                target=self._load_auth_user_thumb,
                args=(self._auth_user_thumb_url,),
                daemon=True
            ).start()

    def _load_auth_user_thumb(self, url):
        """認証ユーザーのサムネイルをダウンロードして表示"""
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # 正方形にセンタークロップしてリサイズ
                size = min(img.width, img.height)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                img = img.resize((32, 32), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                if hasattr(self, 'panel') and self.panel.winfo_exists():
                    self._auth_user_photo = photo  # GC防止
                    self.panel.after(0, lambda: self.lbl_auth_thumb.config(image=photo))
        except Exception as e:
            logger.debug(f"[{self.PLUGIN_NAME}] ユーザーサムネイル取得エラー: {e}")

    def _on_revoke_click(self):
        self._revoke_token()
        self.btn_auth.config(state="normal", text=_t("btn_auth"), bg="#4285f4",
                             command=self._on_auth_click)
        self.lbl_auth_thumb.config(image="")
        self._auth_user_photo = None
        self.lbl_auth_status.config(text=_t("auth_none"), foreground="gray")
        logger.info(f"[{self.PLUGIN_NAME}] {_t('revoke_done')}")

    # ==========================================
    # 配信一覧取得・選択・接続
    # ==========================================
    def _on_fetch_list_click(self):
        """配信一覧を取得ボタン"""
        if not self.is_authenticated:
            self.lbl_status.config(text=_t("status_need_auth"), foreground="red")
            return
        self.btn_fetch_list.config(state="disabled", text=_t("btn_fetching_list"))
        self.lbl_status.config(text=_t("status_fetching"), foreground="orange")
        threading.Thread(target=self._fetch_broadcast_list, daemon=True).start()

    def _fetch_broadcast_list(self):
        """liveBroadcasts.list で配信一覧を取得"""
        try:
            params = {"part": "snippet,status", "broadcastStatus": "upcoming", "maxResults": 50}

            resp = self._youtube.liveBroadcasts().list(**params).execute()
            items = resp.get("items", [])

            self._broadcast_items = []
            for item in items:
                snippet = item.get("snippet", {})
                status = item.get("status", {})
                life_cycle = status.get("lifeCycleStatus", "unknown")

                if life_cycle == "live":
                    status_label = _t("broadcast_active")
                elif life_cycle in ("ready", "created"):
                    status_label = _t("broadcast_upcoming")
                else:
                    status_label = _t("broadcast_other", status=life_cycle)

                thumbs = snippet.get("thumbnails", {})
                thumb_url = None
                for q in ("high", "medium", "default"):
                    if q in thumbs:
                        thumb_url = thumbs[q]["url"]
                        break

                self._broadcast_items.append({
                    "id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:200],
                    "status_label": status_label,
                    "life_cycle": life_cycle,
                    "thumb_url": thumb_url,
                    "scheduled": snippet.get("scheduledStartTime", ""),
                })

            if hasattr(self, 'panel') and self.panel.winfo_exists():
                self.panel.after(0, self._update_broadcast_list_ui)

        except Exception as e:
            # 配信が有効でない等のエラーは空リストとして扱う
            self._broadcast_items = []
            if hasattr(self, 'panel') and self.panel.winfo_exists():
                self.panel.after(0, self._update_broadcast_list_ui)
            logger.info(f"[{self.PLUGIN_NAME}] 配信一覧取得: {e}")

    def _update_broadcast_list_ui(self):
        """取得した配信一覧でリストボックスを更新"""
        self.btn_fetch_list.config(state="normal", text=_t("btn_fetch_list"))
        self.lst_broadcasts.delete(0, tk.END)

        if not self._broadcast_items:
            self.lbl_status.config(text=_t("status_no_broadcasts"), foreground="gray")
            self.btn_connect.config(state="disabled")
            return

        for b in self._broadcast_items:
            self.lst_broadcasts.insert(tk.END, f"{b['status_label']} {b['title']}")

        self.lbl_status.config(text=f"{len(self._broadcast_items)} 件", foreground="blue")
        self.lst_broadcasts.selection_set(0)
        self._on_broadcast_select(None)

    def _on_broadcast_select(self, event):
        """リストボックスの選択が変わったらプレビュー+URLを更新"""
        sel = self.lst_broadcasts.curselection()
        if not sel or sel[0] >= len(self._broadcast_items):
            return
        b = self._broadcast_items[sel[0]]

        # URL欄にリスト選択のIDを反映
        self._var_url.set(f"https://www.youtube.com/watch?v={b['id']}")
        # リスト選択時は確認ボタン不要（既にプレビュー済み）
        self.btn_url_check.config(state="disabled")

        self.lbl_title.config(text=_t("lbl_title", title=b["title"]))
        desc = b["description"]
        self.lbl_desc.config(text=_t("lbl_desc", desc=desc) if desc else _t("lbl_desc_empty"))
        self.btn_connect.config(state="normal")

        thumb_url = b.get("thumb_url")
        if thumb_url:
            threading.Thread(target=self._load_preview_thumbnail, args=(thumb_url,), daemon=True).start()
        else:
            self.lbl_preview.config(image="", text=_t("lbl_thumb_empty"))

        # 権限チェック（バックグラウンド）
        threading.Thread(target=self._check_permission_for_video, args=(b["id"],), daemon=True).start()

    def _on_url_changed(self, *_):
        """URL入力欄の内容が変わったら確認ボタンの状態を更新"""
        url = self._var_url.get().strip()
        # リスト選択由来のURL変更では確認ボタンは不要
        sel = self.lst_broadcasts.curselection() if hasattr(self, 'lst_broadcasts') else ()
        if sel and sel[0] < len(self._broadcast_items):
            selected_url = f"https://www.youtube.com/watch?v={self._broadcast_items[sel[0]]['id']}"
            if url == selected_url:
                self.btn_url_check.config(state="disabled")
                return
        # 手入力の場合は確認ボタンを有効に
        if url:
            self.btn_url_check.config(state="normal")
        else:
            self.btn_url_check.config(state="disabled")

    def _on_url_check_click(self):
        """URL確認ボタン: URLから動画情報を取得してプレビュー表示"""
        if not self.is_authenticated:
            self.lbl_status.config(text=_t("status_need_auth"), foreground="red")
            return
        url = self._var_url.get().strip()
        if not url:
            return
        match = re.search(r"(?:v=|/vi?/|/live/|youtu\.be/)([^&?/\s]{11})", url)
        if not match:
            messagebox.showerror(_t("url_error_title"), _t("url_error_msg"))
            return

        video_id = match.group(1)
        self.btn_url_check.config(state="disabled")
        self.lbl_status.config(text=_t("status_fetching"), foreground="orange")

        # リストの選択を解除
        self.lst_broadcasts.selection_clear(0, tk.END)

        threading.Thread(target=self._check_url_video, args=(video_id,), daemon=True).start()

    def _check_url_video(self, video_id):
        """URL入力の動画情報を取得してプレビューに表示"""
        try:
            resp = self._youtube.videos().list(
                part="snippet,liveStreamingDetails",
                id=video_id
            ).execute()
            items = resp.get("items", [])
            if not items:
                raise ValueError("Video not found")

            snippet = items[0]["snippet"]
            title = snippet.get("title", "")
            desc = snippet.get("description", "")[:200]

            # 内部状態を仮セット（接続ボタン用）
            self._url_check_video_id = video_id
            self._url_check_title = title
            self._url_check_desc = desc

            # サムネイル取得
            thumbs = snippet.get("thumbnails", {})
            thumb_url = None
            for q in ("high", "medium", "default"):
                if q in thumbs:
                    thumb_url = thumbs[q]["url"]
                    break

            if hasattr(self, 'panel') and self.panel.winfo_exists():
                self.panel.after(0, lambda: self._update_url_check_ui(title, desc))
            if thumb_url:
                self._load_preview_thumbnail(thumb_url)

            # 権限チェック（同一スレッド内で実行）
            self._check_permission_for_video(video_id)

        except Exception as e:
            if hasattr(self, 'panel') and self.panel.winfo_exists():
                self.panel.after(0, lambda: self._update_ui_error(str(e)))

    def _update_url_check_ui(self, title, desc):
        self.lbl_title.config(text=_t("lbl_title", title=title))
        self.lbl_desc.config(text=_t("lbl_desc", desc=desc) if desc else _t("lbl_desc_empty"))
        self.lbl_status.config(text="", foreground="gray")
        self.btn_connect.config(state="normal")

    def _check_permission_for_video(self, video_id):
        """配信の権限を判定してUI表示。
        1. チャンネルID比較（オーナー判定）
        2. liveChatModerators.list を試行（管理者判定）"""
        if hasattr(self, 'lbl_permission') and self.lbl_permission.winfo_exists():
            self.panel.after(0, lambda: self.lbl_permission.config(
                text=_t("perm_checking"), foreground="gray"))

        is_owner = False
        try:
            # 動画情報取得
            resp = self._youtube.videos().list(
                part="snippet,liveStreamingDetails", id=video_id
            ).execute()
            items = resp.get("items", [])
            if not items:
                return

            broadcast_channel_id = items[0].get("snippet", {}).get("channelId", "")
            live_chat_id = items[0].get("liveStreamingDetails", {}).get("activeLiveChatId")

            # 方法1: チャンネルID比較（Brand Account本人でログインした場合）
            try:
                my_ch = self._youtube.channels().list(part="id", mine=True).execute()
                my_items = my_ch.get("items", [])
                if my_items and my_items[0]["id"] == broadcast_channel_id:
                    is_owner = True
            except Exception:
                pass

            # 方法2: liveChatModerators.list 試行（管理者権限の検出）
            if not is_owner and live_chat_id:
                try:
                    self._youtube.liveChatModerators().list(
                        liveChatId=live_chat_id, part="id", maxResults=1
                    ).execute()
                    # 成功 = オーナーまたは管理者
                    is_owner = True
                    logger.debug(f"[{self.PLUGIN_NAME}] liveChatModerators.list 成功 → 管理者権限あり")
                except Exception:
                    # 403 = 権限なし
                    pass

        except Exception as e:
            logger.debug(f"[{self.PLUGIN_NAME}] 権限チェックエラー: {e}")

        if hasattr(self, 'panel') and self.panel.winfo_exists():
            self.panel.after(0, lambda: self._update_permission_ui(is_owner))

    def _update_permission_ui(self, is_owner):
        """権限判定結果をUIに反映（ラベル + チェックボックスのグレーアウト）"""
        if hasattr(self, 'lbl_permission') and self.lbl_permission.winfo_exists():
            if is_owner:
                self.lbl_permission.config(text=_t("perm_owner"), foreground="green")
            else:
                self.lbl_permission.config(text=_t("perm_viewer"), foreground="orange")

        # オーナー専用機能: 権限なしならチェックを外してグレーアウト
        if hasattr(self, '_owner_only_checks'):
            for chk in self._owner_only_checks:
                if chk.winfo_exists():
                    if is_owner:
                        chk.state(['!disabled'])
                    else:
                        chk.state(['disabled'])
            if not is_owner:
                self.var_ai_poll.set(False)
                self.var_ai_title.set(False)
                if hasattr(self, 'var_viewer_poll'):
                    self.var_viewer_poll.set(False)
                if hasattr(self, 'var_viewer_title'):
                    self.var_viewer_title.set(False)
                if hasattr(self, '_chk_v_poll'):
                    self._chk_v_poll.configure(state="disabled")
                if hasattr(self, '_chk_v_title'):
                    self._chk_v_title.configure(state="disabled")

    def _set_features_locked(self, locked):
        """ライブ中は機能設定を全ロック/解除"""
        if hasattr(self, '_all_feature_checks'):
            for chk in self._all_feature_checks:
                if chk.winfo_exists():
                    chk.configure(state="disabled" if locked else "normal")
        if hasattr(self, '_all_viewer_checks'):
            for chk in self._all_viewer_checks:
                if chk.winfo_exists():
                    chk.configure(state="disabled" if locked else "normal")

    def _load_preview_thumbnail(self, thumb_url):
        """サムネイルをダウンロードしてプレビューに表示"""
        try:
            img_resp = requests.get(thumb_url, timeout=10)
            if img_resp.status_code == 200:
                img = Image.open(io.BytesIO(img_resp.content))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                preview = img.copy()
                preview.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(preview)
                if hasattr(self, 'panel') and self.panel.winfo_exists():
                    self._preview_photo_ref = photo
                    self.panel.after(0, lambda: self.lbl_preview.config(image=photo, text=""))
        except Exception:
            pass

    def _on_connect_click(self):
        """選択した配信 or URL確認済みの配信に接続"""
        # リスト選択があればリストから
        sel = self.lst_broadcasts.curselection()
        if sel and sel[0] < len(self._broadcast_items):
            b = self._broadcast_items[sel[0]]
            self.video_id = b["id"]
            self.yt_title = b["title"]
            self.yt_desc = b["description"]
        elif hasattr(self, '_url_check_video_id') and self._url_check_video_id:
            # URL確認済みのデータを使用
            self.video_id = self._url_check_video_id
            self.yt_title = getattr(self, '_url_check_title', '')
            self.yt_desc = getattr(self, '_url_check_desc', '')
        else:
            # URLから直接パース
            url = self._var_url.get().strip()
            match = re.search(r"(?:v=|/vi?/|/live/|youtu\.be/)([^&?/\s]{11})", url)
            if not match:
                return
            self.video_id = match.group(1)

        # URL保存
        settings = self.get_settings()
        settings["saved_url"] = self._var_url.get().strip()
        self.save_settings(settings)

        self.btn_connect.config(state="disabled", text=_t("btn_fetching"))
        self.lbl_status.config(text=_t("status_fetching"), foreground="orange")

        threading.Thread(target=self._connect_to_broadcast, daemon=True).start()

    def _connect_to_broadcast(self):
        """選択した配信に接続（liveChatId取得 + 権限判定 + サムネイルDL）"""
        try:
            resp = self._youtube.videos().list(
                part="snippet,liveStreamingDetails",
                id=self.video_id
            ).execute()

            items = resp.get("items", [])
            if items:
                live_details = items[0].get("liveStreamingDetails", {})
                self.live_chat_id = live_details.get("activeLiveChatId")
                broadcast_channel_id = items[0].get("snippet", {}).get("channelId", "")

                thumbs = items[0].get("snippet", {}).get("thumbnails", {})
                thumb_url = None
                for q in ("maxres", "high", "medium", "default"):
                    if q in thumbs:
                        thumb_url = thumbs[q]["url"]
                        break
                if thumb_url:
                    img_resp = requests.get(thumb_url, timeout=10)
                    if img_resp.status_code == 200:
                        img = Image.open(io.BytesIO(img_resp.content))
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        img.thumbnail((1024, 1024))
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=85)
                        self.thumbnail_bytes = buf.getvalue()

                # 権限判定: チャンネルID比較 + liveChatModerators.list 試行
                self._is_owner = False
                try:
                    my_ch = self._youtube.channels().list(part="id", mine=True).execute()
                    my_items = my_ch.get("items", [])
                    if my_items:
                        my_channel_id = my_items[0]["id"]
                        self._is_owner = (my_channel_id == broadcast_channel_id)
                        logger.info(f"[{self.PLUGIN_NAME}] 認証チャンネルID: {my_channel_id}")
                        logger.info(f"[{self.PLUGIN_NAME}] 配信チャンネルID: {broadcast_channel_id}")
                except Exception as e:
                    logger.debug(f"[{self.PLUGIN_NAME}] チャンネルID取得エラー: {e}")

                # チャンネルID不一致でも管理者権限がある場合を検出
                if not self._is_owner and self.live_chat_id:
                    try:
                        self._youtube.liveChatModerators().list(
                            liveChatId=self.live_chat_id, part="id", maxResults=1
                        ).execute()
                        self._is_owner = True
                        logger.info(f"[{self.PLUGIN_NAME}] liveChatModerators.list 成功 → 管理者権限あり")
                    except Exception:
                        pass

                # 権限ログ出力
                logger.info(f"[{self.PLUGIN_NAME}] --- 権限判定 ---")
                logger.info(f"[{self.PLUGIN_NAME}]   オーナー/マネージャー: {'YES' if self._is_owner else 'NO'}")
                logger.info(f"[{self.PLUGIN_NAME}]   コメント読み取り: YES")
                logger.info(f"[{self.PLUGIN_NAME}]   コメント書き込み: YES（try-and-catch）")
                logger.info(f"[{self.PLUGIN_NAME}]   アンケート作成:   {'YES' if self._is_owner else 'NO'}")
                logger.info(f"[{self.PLUGIN_NAME}]   タイトル変更:     {'YES' if self._is_owner else 'NO'}")
                logger.info(f"[{self.PLUGIN_NAME}]   視聴者数取得:     YES")
                logger.info(f"[{self.PLUGIN_NAME}] ----------------")

            self.is_connected = True
            self._update_enabled_state(True)

            if hasattr(self, 'panel') and self.panel.winfo_exists():
                self.panel.after(0, self._update_ui_connected)

            if self._live_queue is not None and not self.is_running:
                self.start(self._live_prompt_config, self._live_queue, mid_session=True)

            logger.info(f"[{self.PLUGIN_NAME}] 接続成功: {self.yt_title} (chatId: {self.live_chat_id})")

        except Exception as e:
            self.video_id = None
            self._update_enabled_state(False)
            if hasattr(self, 'panel') and self.panel.winfo_exists():
                self.panel.after(0, lambda: self._update_ui_error(str(e)))
            logger.warning(f"[{self.PLUGIN_NAME}] 接続エラー: {e}")

    def _update_enabled_state(self, is_enabled):
        settings = self.get_settings()
        settings["enabled"] = is_enabled
        self.save_settings(settings)

    def _update_ui_connected(self):
        if hasattr(self, 'btn_connect'):
            self.btn_connect.pack_forget()
        if hasattr(self, 'btn_disconnect'):
            self.btn_disconnect.pack(side="left")
        if hasattr(self, 'lst_broadcasts'):
            self.lst_broadcasts.config(state="disabled")
        if hasattr(self, 'btn_fetch_list'):
            self.btn_fetch_list.config(state="disabled")
        if hasattr(self, 'btn_url_check'):
            self.btn_url_check.config(state="disabled")
        if hasattr(self, 'ent_url'):
            self.ent_url.config(state="readonly")
        self.lbl_status.config(text=_t("status_connected", video_id=self.video_id), foreground="green")
        self.lbl_title.config(text=_t("lbl_title", title=self.yt_title))
        self.lbl_desc.config(text=_t("lbl_desc", desc=self.yt_desc))

    def _update_ui_error(self, err_msg):
        if hasattr(self, 'btn_connect'):
            self.btn_connect.config(state="normal", text=_t("btn_connect"))
        if hasattr(self, 'btn_fetch_list'):
            self.btn_fetch_list.config(state="normal", text=_t("btn_fetch_list"))
        self.lbl_status.config(text=_t("status_error", err_msg=err_msg), foreground="red")

    def _disconnect(self):
        self.is_running = False
        if self.thumb_thread:
            self.thumb_thread.cancel()
        self.is_connected = False
        self.video_id = None
        self.live_chat_id = None
        self.yt_title = ""
        self.yt_desc = ""
        self.thumbnail_bytes = None
        self._chat_page_token = None
        self._active_poll_id = None
        self._is_owner = False

        self._update_enabled_state(False)

        if hasattr(self, 'btn_disconnect'):
            self.btn_disconnect.pack_forget()
        if hasattr(self, 'btn_connect'):
            self.btn_connect.config(state="disabled", text=_t("btn_connect"))
            self.btn_connect.pack(side="left")
        if hasattr(self, 'lst_broadcasts'):
            self.lst_broadcasts.config(state="normal")
        if hasattr(self, 'btn_fetch_list'):
            self.btn_fetch_list.config(state="normal")
        if hasattr(self, 'btn_url_check'):
            self.btn_url_check.config(state="normal")
        if hasattr(self, 'ent_url'):
            self.ent_url.config(state="normal")
        self.lbl_status.config(text=_t("status_disconnected"), foreground="gray")
        self.lbl_title.config(text=_t("lbl_title_empty"))
        self.lbl_desc.config(text=_t("lbl_desc_empty"))
        self.lbl_preview.config(image="", text=_t("lbl_thumb_empty"))
        logger.info(f"[{self.PLUGIN_NAME}] 切断しました。")

        logger.info(f"[{self.PLUGIN_NAME}] 切断しました。")

    # ==========================================
    # AI連携 (プロンプト・ライフサイクル)
    # ==========================================
    def get_prompt_addon(self):
        if not self.is_connected or not self.video_id:
            return ""

        addon = _t("prompt_addon", title=self.yt_title, desc=self.yt_desc)

        # 各機能のチェック状態に応じて個別にプロンプトを組み立て
        settings = self.get_settings()
        cmds = []
        triggers = []

        if settings.get("ai_comment"):
            cmds.append("* コメント書き込み: [CMD]YT:comment コメント内容")
            triggers.append("* 「○○ってコメントして」→ [CMD]YT:comment ○○")

        if settings.get("ai_poll") and self._is_owner:
            cmds.append("* アンケート作成: [CMD]YT:poll create 質問文|選択肢1|選択肢2|選択肢3")
            cmds.append("* アンケート締切: [CMD]YT:poll close")
            triggers.append("* 「アンケートして」→ [CMD]YT:poll create 質問|A|B|C")
            triggers.append("* 「集計して」→ [CMD]YT:poll close")

        if settings.get("ai_title") and self._is_owner:
            cmds.append("* 配信タイトル変更: [CMD]YT:title 新しいタイトル")
            triggers.append("* 「タイトル変えて」→ [CMD]YT:title 新しいタイトル")

        # 視聴者数は常に有効
        cmds.append("* 視聴者数取得: [CMD]YT:viewers")
        triggers.append("* 「今何人？」→ [CMD]YT:viewers")

        if cmds:
            addon += "\n# 【YouTube操作コマンド】\n"
            addon += "テロップテキストの末尾（[MEMO]の直前）に記述してください。\n"
            addon += "\n".join(cmds) + "\n"
            addon += "\n## 配信者の発言に対する反応ルール\n"
            addon += "\n".join(triggers) + "\n"
            # 視聴者コメントからの実行権限（設定に応じて動的生成）
            viewer_ok = ["[CMD]YT:viewers"]
            viewer_ng = []
            if settings.get("viewer_comment"):
                viewer_ok.append("[CMD]YT:comment")
            else:
                viewer_ng.append("[CMD]YT:comment")
            for cmd, key in [("[CMD]YT:poll", "viewer_poll"), ("[CMD]YT:title", "viewer_title")]:
                if settings.get(key):
                    viewer_ok.append(cmd)
                else:
                    viewer_ng.append(cmd)
            addon += "\n## 視聴者コメントからの実行権限\n"
            if viewer_ok:
                addon += f"* 視聴者コメントからも実行可: {' / '.join(viewer_ok)}\n"
            if viewer_ng:
                addon += f"* 配信者の音声指示のみ（視聴者コメントでは実行禁止）: {' / '.join(viewer_ng)}\n"

        return addon

    def start(self, prompt_config, plugin_queue, mid_session=False):
        self._live_queue = plugin_queue
        self._live_prompt_config = prompt_config

        if not self.is_connected or not self.video_id:
            logger.debug(f"[{self.PLUGIN_NAME}] URL未接続のため待機")
            return

        self.cmt_msg = prompt_config.get("CMT_MSG", "")
        self.ai_name = prompt_config.get("ai_name", "AI")
        self.plugin_queue = plugin_queue
        self.is_running = True

        # ライブ中は機能設定をロック
        if hasattr(self, 'panel') and self.panel.winfo_exists():
            self.panel.after(0, lambda: self._set_features_locked(True))

        # サムネイル注入
        if self.thumbnail_bytes:
            self.thumb_thread = threading.Timer(5.0, self._inject_thumbnail)
            self.thumb_thread.daemon = True
            self.thumb_thread.start()

        # コメント取得スレッド
        settings = self.get_settings()
        if settings.get("fetch_comments", True) and self.live_chat_id:
            self.chat_thread = threading.Thread(target=self._chat_loop, daemon=True)
            self.chat_thread.start()

        # ライブ中の後接続: system_instructionには入れられないのでメッセージとして注入
        if mid_session:
            prompt = self.get_prompt_addon()
            if prompt and self.plugin_queue:
                self.send_text(self.plugin_queue, prompt)
                logger.info(f"[{self.PLUGIN_NAME}] ライブ中後接続: プロンプトをメッセージ注入")

        logger.info(f"[{self.PLUGIN_NAME}] ライブ連携開始 (ID: {self.video_id})")

    def stop(self):
        self.is_running = False
        self._live_queue = None
        self._live_prompt_config = None
        if self.thumb_thread:
            self.thumb_thread.cancel()
        self._chat_page_token = None

        # ライブ終了時に機能設定のロック解除
        if hasattr(self, 'panel') and self.panel.winfo_exists():
            self.panel.after(0, lambda: self._set_features_locked(False))

        logger.info(f"[{self.PLUGIN_NAME}] ライブ連携停止")

    def _inject_thumbnail(self):
        if not self.is_running or not self.plugin_queue:
            return
        self.plugin_queue.put({
            "type": "image",
            "data": self.thumbnail_bytes,
            "mime_type": "image/jpeg"
        })
        self.plugin_queue.put({
            "type": "text",
            "content": _t("thumb_cue")
        })
        logger.info(f"[{self.PLUGIN_NAME}] サムネイルをAIに注入")

    # ==========================================
    # コメント取得ループ (YouTube Data API)
    # ==========================================
    def _chat_loop(self):
        """liveChatMessages.list でコメントをポーリング"""
        # スレッド専用の YouTube サービスを作成（httplib2 はスレッドセーフでない）
        yt_chat = self._build_youtube_service()
        if not yt_chat:
            logger.error(f"[{self.PLUGIN_NAME}] チャット用サービス作成失敗")
            return
        logger.info(f"[{self.PLUGIN_NAME}] コメント取得ループ開始 (chatId: {self.live_chat_id})")

        while self.is_running:
            try:
                params = {
                    "liveChatId": self.live_chat_id,
                    "part": "snippet,authorDetails",
                    "maxResults": 200,
                }
                if self._chat_page_token:
                    params["pageToken"] = self._chat_page_token

                resp = yt_chat.liveChatMessages().list(**params).execute()
                self._chat_page_token = resp.get("nextPageToken")
                polling_ms = resp.get("pollingIntervalMillis", 5000)

                items = resp.get("items", [])
                if items:
                    comments = []
                    avatar_map = {}
                    for item in items:
                        snippet = item.get("snippet", {})
                        author = item.get("authorDetails", {})
                        msg_type = snippet.get("type", "")

                        if msg_type == "textMessageEvent":
                            text_detail = snippet.get("textMessageDetails", {})
                            text = text_detail.get("messageText", "")
                            if len(text) > 100:
                                text = text[:100] + "..."
                            name = author.get("displayName", "unknown")
                            comments.append(f"[COMMENT] {name}: {text}")

                            avatar_url = author.get("profileImageUrl", "")
                            if avatar_url:
                                avatar_map[name] = avatar_url

                    if comments and self.plugin_queue:
                        self.send_avatar_map(self.plugin_queue, avatar_map)
                        combined = "\n".join(comments)
                        count_prefix = f"({len(comments)}件)\n" if len(comments) > 1 else ""
                        payload = f"{count_prefix}{combined}"
                        if self.cmt_msg:
                            payload += f"\n\n{self.cmt_msg}"
                        self.send_text(self.plugin_queue, payload)
                        logger.info(f"[{self.PLUGIN_NAME}] コメント注入 ({len(comments)}件)")

                # APIが推奨するポーリング間隔で待機
                wait_sec = max(polling_ms / 1000.0, 3.0)
                for _ in range(int(wait_sec)):
                    if not self.is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.warning(f"[{self.PLUGIN_NAME}] コメント取得エラー: {e}")
                for _ in range(10):
                    if not self.is_running:
                        break
                    time.sleep(1)

        logger.info(f"[{self.PLUGIN_NAME}] コメント取得ループ終了")

    # ==========================================
    # CMD ハンドラー: [CMD]YT:xxx
    # ==========================================
    def setup(self, cfg) -> bool:
        """CMD登録時のバリデーション（常に有効）"""
        return True

    @staticmethod
    def _clean_cmd_value(value: str) -> str:
        """CMD値からテロップタグを除去する。
        AI出力が [CMD]YT:comment こんにちは[WND]window-simple[LAY]... のように
        テロップタグが混入する場合があるため、最初の[タグ]以降を切り捨てる。"""
        cleaned = re.sub(r'\[(?:WND|LAY|BDG|MEMO|TOPIC|MAIN)\].*$', '', value, flags=re.IGNORECASE)
        return cleaned.strip()

    def handle(self, value: str):
        """[CMD]YT:サブコマンド を処理"""
        if not value:
            return

        value = self._clean_cmd_value(value)
        if not value:
            return

        # CMD はメインスレッドとは別スレッドから呼ばれるため、専用サービスを作成
        yt_cmd = self._build_youtube_service()
        if not yt_cmd:
            logger.warning(f"[{self.PLUGIN_NAME}] CMD用サービス作成失敗")
            return

        # スペースありでもなしでもマッチするようプレフィックスで判定
        v = value.strip()
        v_lower = v.lower()
        matched = False
        for cmd_name, handler in [
            ("comment", lambda a: self._cmd_comment(a, yt_cmd)),
            ("poll", lambda a: self._cmd_poll(a, yt_cmd)),
            ("title", lambda a: self._cmd_title(a, yt_cmd)),
            ("viewers", lambda a: self._cmd_viewers(yt_cmd)),
        ]:
            if v_lower.startswith(cmd_name):
                arg = v[len(cmd_name):].strip()
                handler(arg)
                matched = True
                break
        if not matched:
            logger.warning(f"[{self.PLUGIN_NAME}] 未知のサブコマンド: '{v}'")

    def _cmd_title(self, new_title, yt_service):
        """配信タイトルを変更する"""
        settings = self.get_settings()
        if not settings.get("ai_title", True):
            return
        if not self.is_authenticated or not self.video_id or not new_title:
            return
        try:
            yt_service.videos().update(
                part="snippet",
                body={
                    "id": self.video_id,
                    "snippet": {
                        "title": new_title.strip(),
                        "categoryId": "22",  # People & Blogs（必須フィールド）
                    }
                }
            ).execute()
            self.yt_title = new_title.strip()
            logger.info(f"[{self.PLUGIN_NAME}] {_t('title_changed', title=new_title.strip())}")
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('title_error', err=str(e))}")

    def _cmd_viewers(self, yt_service):
        """現在の同時視聴者数を取得してAIにフィードバック"""
        if not self.is_authenticated or not self.video_id:
            return

        try:
            resp = yt_service.videos().list(
                part="liveStreamingDetails",
                id=self.video_id
            ).execute()

            items = resp.get("items", [])
            if items:
                live_details = items[0].get("liveStreamingDetails", {})
                count = live_details.get("concurrentViewers")
                if count is not None:
                    cue = _t("viewers_cue", count=count)
                    logger.info(f"[{self.PLUGIN_NAME}] 同時視聴者数: {count}")
                else:
                    cue = _t("viewers_unavailable")
                    logger.info(f"[{self.PLUGIN_NAME}] concurrentViewers が取得できず")
            else:
                cue = _t("viewers_unavailable")
                logger.warning(f"[{self.PLUGIN_NAME}] 動画情報が見つかりません")

            if self.plugin_queue:
                logger.debug(f"[{self.PLUGIN_NAME}] viewers注入: {cue}")
                self.send_text(self.plugin_queue, cue)

        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('viewers_error', err=str(e))}")

    def _cmd_comment(self, text, yt_service):
        """チャットにコメントを書き込む"""
        settings = self.get_settings()
        if not settings.get("ai_comment", True):
            return
        if not self.is_authenticated or not self.live_chat_id or not text:
            return

        try:
            yt_service.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": text.strip()
                        }
                    }
                }
            ).execute()
            logger.info(f"[{self.PLUGIN_NAME}] {_t('comment_sent', text=text[:50])}")
        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('comment_error', err=str(e))}")

    def _cmd_poll(self, arg, yt_service):
        """アンケート操作: create / close"""
        settings = self.get_settings()
        if not settings.get("ai_poll", True):
            return
        if not self.is_authenticated or not self.live_chat_id:
            return

        parts = arg.strip().split(None, 1)
        action = parts[0].lower() if parts else ""
        param = parts[1] if len(parts) > 1 else ""

        if action == "create":
            self._poll_create(param, yt_service)
        elif action == "close":
            self._poll_close(yt_service)
        else:
            logger.warning(f"[{self.PLUGIN_NAME}] 未知のpollアクション: {action}")

    def _poll_create(self, param, yt_service):
        """アンケート作成: 質問文|選択肢1|選択肢2|..."""
        segments = [s.strip() for s in param.split("|") if s.strip()]
        if len(segments) < 3:
            logger.warning(f"[{self.PLUGIN_NAME}] poll create: 質問+選択肢2個以上が必要")
            return
        if len(segments) > 5:
            segments = segments[:5]  # 質問 + 最大4選択肢

        question = segments[0]
        options = segments[1:]

        try:
            resp = yt_service.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "pollEvent",
                        "pollDetails": {
                            "metadata": {
                                "questionText": question,
                                "options": [{"optionText": opt} for opt in options]
                            }
                        }
                    }
                }
            ).execute()

            self._active_poll_id = resp.get("id")
            self._active_poll_question = question
            logger.info(f"[{self.PLUGIN_NAME}] {_t('poll_created', question=question)}")

        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('poll_create_error', err=str(e))}")

    def _poll_close(self, yt_service):
        """アンケート締切 + 集計結果をAIにフィードバック"""
        if not self._active_poll_id:
            logger.info(f"[{self.PLUGIN_NAME}] {_t('poll_no_active')}")
            return

        try:
            # Poll を閉じる
            yt_service.liveChatMessages().transition(
                id=self._active_poll_id,
                status="closed"
            ).execute()
            logger.info(f"[{self.PLUGIN_NAME}] {_t('poll_closed')}")
            logger.debug(f"[{self.PLUGIN_NAME}] active_poll_id={self._active_poll_id}")

            # close直後はAPIに反映されるまで少し待つ
            time.sleep(2)

            # 結果取得: liveChatMessages.list でpollの結果を含むメッセージを取得
            resp = yt_service.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet",
                maxResults=200,
            ).execute()

            # pollEvent / pollClosedDetails から結果を探す
            logger.debug(f"[{self.PLUGIN_NAME}] poll close後のAPI応答 items数={len(resp.get('items', []))}")
            for item in resp.get("items", []):
                s = item.get("snippet", {})
                logger.debug(f"  type={s.get('type')} id={item.get('id')}")
                if s.get("type") == "pollEvent":
                    pd = s.get("pollDetails", {})
                    logger.debug(f"    pollDetails={json.dumps(pd, ensure_ascii=False, default=str)}")

            result_text = ""
            for item in reversed(resp.get("items", [])):
                snippet = item.get("snippet", {})
                item_type = snippet.get("type", "")

                # pollClosedDetails, pollEvent, またはIDが一致するアイテム
                if item_type in ("pollClosedDetails", "pollEvent") or item.get("id") == self._active_poll_id:
                    poll_details = snippet.get("pollDetails", {})
                    metadata = poll_details.get("metadata", {})
                    question = metadata.get("questionText", self._active_poll_question)
                    options = metadata.get("options", [])

                    if options:
                        lines = [_t("poll_result_header", question=question)]
                        for opt in options:
                            name = opt.get("optionText", "?")
                            count = opt.get("tally", 0)
                            lines.append(_t("poll_result_line", option=name, count=count))
                        result_text = "\n".join(lines)
                        break

            if not result_text:
                result_text = _t("poll_result_header", question=self._active_poll_question) + "(集計取得待ち)"

            # AIにフィードバック
            if self.plugin_queue:
                cue = _t("poll_result_cue", results=result_text)
                logger.debug(f"[{self.PLUGIN_NAME}] 注入内容:\n{cue}")
                self.send_text(self.plugin_queue, cue)
                logger.info(f"[{self.PLUGIN_NAME}] アンケート結果をAIに送信")
            else:
                logger.warning(f"[{self.PLUGIN_NAME}] plugin_queueが未設定のためAI注入できず")

            self._active_poll_id = None
            self._active_poll_question = ""

        except Exception as e:
            logger.warning(f"[{self.PLUGIN_NAME}] {_t('poll_close_error', err=str(e))}")

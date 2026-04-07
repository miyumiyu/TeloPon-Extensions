"""
軽量 NDGR クライアント — TeloPon ニコニコ配信プラグイン用
NDGRClient (MIT License) のプロトコル仕様を参考に aiohttp + websockets で再実装。
curl-cffi 不要。コメント・ギフト・広告・統計・アンケートなど全メッセージを処理する。

ref: https://github.com/tsukumijima/NDGRClient
ref: https://github.com/rinsuki-lab/ndgr-reader
"""

from __future__ import annotations

import asyncio
import json
import re
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

import aiohttp
import websockets

from _niconico.proto.dwango.nicolive.chat.service.edge import payload_pb2 as chat
from _niconico.proto.dwango.nicolive.chat.data import atoms_pb2 as atoms
from _niconico.proto.dwango.nicolive.chat.data.atoms import notifications_pb2
from _niconico.stream_reader import ProtobufStreamReader

# Enquete Status は Nested enum のため直接マッピング
_ENQUETE_STATUS = {0: "Closed", 1: "Poll", 2: "Result"}

import logger


# ---------------------------------------------------------------------------
# データモデル
# ---------------------------------------------------------------------------
@dataclass
class ProgramInfo:
    """配信番組の基本情報"""
    program_id: str        # lv...
    title: str
    description: str
    status: str            # ON_AIR / ENDED
    begin_time: int
    end_time: int
    vpos_base_time: int
    web_socket_url: str
    supplier_id: str = ""   # 配信者のユーザーID (ユーザー生放送のみ)
    supplier_name: str = "" # 配信者名
    thumbnail_url: str = "" # サムネイルURL


@dataclass
class NicoComment:
    """コメント"""
    content: str
    user_id: str            # hashed or raw
    raw_user_id: int = 0
    no: int = 0
    at: datetime | None = None
    is_premium: bool = False
    name: str = ""          # コテハン（放送内ニックネーム、未設定なら空）
    avatar_url: str = ""    # ユーザーアイコンURL（184は空）


@dataclass
class NicoGift:
    """ギフト"""
    advertiser_name: str
    item_name: str
    point: int
    contribution_rank: int = 0


@dataclass
class NicoAd:
    """ニコニ広告"""
    advertiser_name: str
    point: int
    message: str = ""


@dataclass
class NicoEnquete:
    """アンケート状態"""
    question: str
    choices: list[str] = field(default_factory=list)
    results_per_mille: list[int] = field(default_factory=list)
    status: str = ""       # Poll / Result / Closed


@dataclass
class NicoStatistics:
    """リアルタイム統計"""
    viewers: int = 0
    comments: int = 0
    ad_points: int = 0
    gift_points: int = 0


@dataclass
class NicoNotification:
    """SimpleNotification / SimpleNotificationV2"""
    type: str              # EMOTION, CRUISE, RANKING_IN, VISITED, USER_FOLLOW, ...
    message: str = ""


# ---------------------------------------------------------------------------
# コールバック型
# ---------------------------------------------------------------------------
@dataclass
class NicoCallbacks:
    on_comment: Callable[[NicoComment], Any] | None = None
    on_gift: Callable[[NicoGift], Any] | None = None
    on_ad: Callable[[NicoAd], Any] | None = None
    on_enquete: Callable[[NicoEnquete], Any] | None = None
    on_statistics: Callable[[NicoStatistics], Any] | None = None
    on_notification: Callable[[NicoNotification], Any] | None = None


# ---------------------------------------------------------------------------
# HTTP ヘッダー
# ---------------------------------------------------------------------------
_HTTP_HEADERS = {
    "accept": "*/*",
    "accept-language": "ja",
    "origin": "https://live.nicovideo.jp",
    "referer": "https://live.nicovideo.jp/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}

_TAG = "[NicoClient]"


# ---------------------------------------------------------------------------
# NicoLiveClient
# ---------------------------------------------------------------------------
class NicoLiveClient:
    """ニコニコ生放送 NDGR クライアント (軽量版)"""

    def __init__(self, callbacks: NicoCallbacks | None = None):
        self.callbacks = callbacks or NicoCallbacks()
        self._session: aiohttp.ClientSession | None = None
        self._cookies: dict[str, str] = {}
        self._running = False

    # ---- 認証 ----

    async def login(
        self,
        *,
        mail: str | None = None,
        password: str | None = None,
        user_session: str | None = None,
    ) -> bool | str:
        """
        ニコニコにログイン (配信者API用)。読み取り専用なら不要。

        Returns:
            True: ログイン成功
            False: ログイン失敗
            str (MFA URL): 2FA が必要 — この URL に OTP を送信する必要がある
        """
        session = await self._ensure_session()
        if user_session:
            self._cookies["user_session"] = user_session
            self._set_cookie(session, "user_session", user_session)
            return True

        if mail and password:
            async with session.post(
                "https://account.nicovideo.jp/login/redirector?site=niconico",
                data={"mail_tel": mail, "password": password},
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                # user_session Cookie があればログイン成功（2FA なし）
                if self._extract_user_session(session):
                    return True
                # MFA ページにリダイレクトされた場合
                final_url = str(resp.url)
                if "/mfa" in final_url:
                    self._mfa_url = final_url
                    return final_url  # 呼び出し元に MFA URL を返す
            return False
        return False

    async def submit_mfa(self, otp: str) -> bool:
        """2FA の OTP コードを送信する。login() が MFA URL を返した後に呼ぶ。"""
        session = await self._ensure_session()
        mfa_url = getattr(self, "_mfa_url", None)
        if not mfa_url:
            return False
        async with session.post(
            mfa_url,
            data={
                "otp": otp,
                "loginBtn": "Login",
                "is_mfa_trusted_device": "true",
                "device_name": "TeloPon",
            },
            allow_redirects=True,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if self._extract_user_session(session):
                return True
            # 200 が返った場合は OTP が間違っている
            return False

    def _extract_user_session(self, session: aiohttp.ClientSession) -> bool:
        """Cookie から user_session を抽出して保存する。"""
        for cookie in session.cookie_jar:
            if cookie.key == "user_session":
                self._cookies["user_session"] = cookie.value
                return True
        return False

    @property
    def is_logged_in(self) -> bool:
        return bool(self._cookies.get("user_session"))

    # ---- ユーザー情報取得 ----

    async def fetch_my_profile(self) -> dict | None:
        """
        ログイン中のユーザーのプロフィール情報を取得する。
        Returns: {"nickname": str, "icon_url": str, "user_id": int} or None
        """
        session = await self._ensure_session()
        try:
            async with session.get(
                "https://nvapi.nicovideo.jp/v1/users/me",
                headers={
                    **_HTTP_HEADERS,
                    "X-Frontend-Id": "6",
                    "X-Frontend-Version": "0",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                user = data.get("data", {}).get("user", {})
                icons = user.get("icons", {})
                return {
                    "nickname": user.get("nickname", ""),
                    "icon_url": icons.get("small", "") or icons.get("large", ""),
                    "user_id": user.get("id", 0),
                }
        except Exception as e:
            logger.debug(f"{_TAG} プロフィール取得エラー: {e}")
            return None

    # ---- 配信情報取得 ----

    async def fetch_program_info(self, nicolive_id: str) -> ProgramInfo:
        """視聴ページから配信情報を取得する。"""
        session = await self._ensure_session()
        url = f"https://live.nicovideo.jp/watch/{nicolive_id}"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            resp.raise_for_status()
            html = await resp.text()

        # embedded-data の data-props JSON を正規表現で抽出
        m = re.search(r'id="embedded-data"\s+data-props="([^"]+)"', html)
        if not m:
            raise ValueError("embedded-data が見つかりません")
        import html as html_mod
        props = json.loads(html_mod.unescape(m.group(1)))

        prog = props["program"]
        site = props["site"]
        supplier = prog.get("supplier", {})
        thumb = prog.get("thumbnail", {})
        # huge > large > small の優先順で取得（hugeはdict内にURL）
        huge = thumb.get("huge", {})
        large = thumb.get("large", "")
        small = thumb.get("small", "")
        # community-icon はデフォルト画像なので除外
        if "community-icon" in large:
            large = ""
        if "community-icon" in small:
            small = ""
        thumb_url = (
            huge.get("s640x360", "")
            or huge.get("s352x198", "")
            or huge.get("s1280x720", "")
            or large
            or small
        )
        return ProgramInfo(
            program_id=prog["nicoliveProgramId"],
            title=prog["title"],
            description=prog.get("description", ""),
            status=prog["status"],
            begin_time=prog["beginTime"],
            end_time=prog["endTime"],
            vpos_base_time=prog["vposBaseTime"],
            web_socket_url=site["relive"]["webSocketUrl"],
            supplier_id=str(supplier.get("programProviderId", "")),
            supplier_name=supplier.get("name", ""),
            thumbnail_url=thumb_url,
        )

    # ---- WebSocket → NDGR View URI 取得 ----

    async def _fetch_view_uri(self, ws_url: str) -> str:
        """WebSocket 接続して NDGR View API の URI を取得する。"""
        async with websockets.connect(
            ws_url,
            user_agent_header=_HTTP_HEADERS["user-agent"],
            open_timeout=15,
            close_timeout=5,
            ping_timeout=15,
        ) as ws:
            await ws.send(json.dumps({
                "type": "startWatching",
                "data": {"reconnect": False},
            }))
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=15)
                data = json.loads(msg)
                if data["type"] == "messageServer":
                    return data["data"]["viewUri"]

    # ---- Protobuf ストリーム読み取り ----

    async def _fetch_protobuf_stream(self, uri: str, pb_class: type):
        """Protobuf ストリームを HTTP GET して yield する。"""
        session = await self._ensure_session()
        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with session.get(
                    uri,
                    headers=_HTTP_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=60, sock_read=45),
                ) as resp:
                    resp.raise_for_status()
                    reader = ProtobufStreamReader()
                    async for chunk in resp.content.iter_any():
                        reader.add_chunk(chunk)
                        while True:
                            raw = reader.next_message()
                            if raw is None:
                                break
                            pb = pb_class()
                            pb.ParseFromString(raw)
                            yield pb
                break  # 成功
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"{_TAG} ストリーム取得リトライ ({attempt+1}/{max_retries}): {e}")
                    await asyncio.sleep(3)
                else:
                    raise

    # ---- メッセージ処理 ----

    def _process_chunked_message(self, cm: chat.ChunkedMessage):
        """ChunkedMessage を解析し、適切なコールバックを呼ぶ。"""
        # --- コメント ---
        if cm.HasField("message"):
            msg = cm.message
            # Chat / OverflowedChat
            chat_data = None
            if msg.HasField("chat"):
                chat_data = msg.chat
            elif msg.HasField("overflowed_chat"):
                chat_data = msg.overflowed_chat
            if chat_data and self.callbacks.on_comment:
                raw_uid = chat_data.raw_user_id
                user_id = str(raw_uid) if raw_uid > 0 else chat_data.hashed_user_id
                at = None
                if cm.HasField("meta") and cm.meta.HasField("at"):
                    at = datetime.fromtimestamp(
                        cm.meta.at.seconds + cm.meta.at.nanos / 1e9
                    )
                # アバターURL: 非匿名(raw_user_id > 0)なら生成可能
                avatar_url = ""
                if raw_uid > 0:
                    avatar_url = f"https://secure-dcdn.cdn.nimg.jp/nicoaccount/usericon/{raw_uid // 10000}/{raw_uid}.jpg"
                self.callbacks.on_comment(NicoComment(
                    content=chat_data.content,
                    user_id=user_id,
                    raw_user_id=raw_uid,
                    no=chat_data.no,
                    at=at,
                    is_premium=(chat_data.account_status == atoms.Chat.AccountStatus.Premium),
                    name=chat_data.name if chat_data.name else "",
                    avatar_url=avatar_url,
                ))
                return  # コメントは排他（他のフィールドは見ない）

            # Gift
            if msg.HasField("gift") and self.callbacks.on_gift:
                g = msg.gift
                self.callbacks.on_gift(NicoGift(
                    advertiser_name=g.advertiser_name,
                    item_name=g.item_name,
                    point=g.point,
                    contribution_rank=g.contribution_rank if g.contribution_rank else 0,
                ))
                return

            # Nicoad
            if msg.HasField("nicoad") and self.callbacks.on_ad:
                nad = msg.nicoad
                # V0 形式 (latest: advertiser/point/message, total_point)
                if nad.HasField("v0"):
                    self.callbacks.on_ad(NicoAd(
                        advertiser_name=nad.v0.latest.advertiser if nad.v0.HasField("latest") else "",
                        point=nad.v0.total_point if nad.v0.total_point else 0,
                        message=nad.v0.latest.message if nad.v0.HasField("latest") else "",
                    ))
                # V1 形式 (total_ad_point, message)
                elif nad.HasField("v1"):
                    self.callbacks.on_ad(NicoAd(
                        advertiser_name="",
                        point=nad.v1.total_ad_point if nad.v1.total_ad_point else 0,
                        message=nad.v1.message if nad.v1.message else "",
                    ))
                return

            # SimpleNotificationV2
            if msg.HasField("simple_notification_v2") and self.callbacks.on_notification:
                sn = msg.simple_notification_v2
                type_name = notifications_pb2.SimpleNotificationV2.NotificationType.Name(sn.type) if sn.type else "UNKNOWN"
                self.callbacks.on_notification(NicoNotification(
                    type=type_name,
                    message=sn.message if sn.message else "",
                ))
                return

            # SimpleNotification (legacy)
            if msg.HasField("simple_notification") and self.callbacks.on_notification:
                sn = msg.simple_notification
                self.callbacks.on_notification(NicoNotification(
                    type="LEGACY",
                    message=sn.message if sn.message else "",
                ))
                return

        # --- 状態系 ---
        if cm.HasField("state"):
            st = cm.state
            # Statistics
            if st.HasField("statistics") and self.callbacks.on_statistics:
                s = st.statistics
                self.callbacks.on_statistics(NicoStatistics(
                    viewers=s.viewers if s.viewers else 0,
                    comments=s.comments if s.comments else 0,
                    ad_points=s.ad_points if s.ad_points else 0,
                    gift_points=s.gift_points if s.gift_points else 0,
                ))
            # Enquete
            if st.HasField("enquete") and self.callbacks.on_enquete:
                eq = st.enquete
                status_name = _ENQUETE_STATUS.get(eq.status, "Closed")
                choices = [c.description for c in eq.choices]
                results = [c.per_mille for c in eq.choices]
                self.callbacks.on_enquete(NicoEnquete(
                    question=eq.question if eq.question else "",
                    choices=choices,
                    results_per_mille=results,
                    status=status_name,
                ))

    # ---- メインストリーミングループ ----

    async def stream(self, nicolive_id: str):
        """
        指定した番組のリアルタイムメッセージをストリーミングする。
        self._running が False になるか、番組が終了するまで返らない。
        配信開始前の場合は開始まで待機する。
        """
        self._running = True

        while self._running:
            try:
                info = await self.fetch_program_info(nicolive_id)
                if info.status == "ENDED":
                    logger.info(f"{_TAG} 番組は終了しています: {info.program_id}")
                    break
                if not info.web_socket_url:
                    # 配信開始前 — 30秒ごとにリトライ
                    logger.info(f"{_TAG} 配信開始待機中... (status={info.status})")
                    await asyncio.sleep(30)
                    continue

                logger.info(f"{_TAG} 接続開始: {info.title} ({info.program_id})")
                view_uri = await self._fetch_view_uri(info.web_socket_url)
                await self._stream_loop(view_uri)

            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self._running:
                    break
                logger.warning(f"{_TAG} ストリーム異常、10秒後にリトライ: {e}")
                logger.debug(traceback.format_exc())
                await asyncio.sleep(10)

    async def _stream_loop(self, view_uri: str):
        """View API → Segment のポーリングループ"""
        at_param: str = "now"  # 初回は必ず ?at=now
        segment_tasks: dict[str, asyncio.Task] = {}

        try:
            while self._running:
                # View API にアクセスして ChunkedEntry を取得
                url = f"{view_uri}?at={at_param}"
                async for entry in self._fetch_protobuf_stream(url, chat.ChunkedEntry):
                    if not self._running:
                        break

                    # Segment: コメント等を含むセグメントの URI を取得
                    if entry.HasField("segment"):
                        seg_uri = entry.segment.uri
                        if seg_uri and seg_uri not in segment_tasks:
                            task = asyncio.create_task(self._fetch_segment(seg_uri))
                            segment_tasks[seg_uri] = task

                    # ReadyForNext: 次回ポーリングのタイムスタンプ
                    if entry.HasField("next"):
                        at_param = str(entry.next.at)

                # 完了したタスクを掃除
                done_keys = [k for k, t in segment_tasks.items() if t.done()]
                for k in done_keys:
                    t = segment_tasks.pop(k)
                    if t.exception():
                        logger.warning(f"{_TAG} セグメントエラー: {t.exception()}")

        finally:
            for t in segment_tasks.values():
                t.cancel()
            await asyncio.gather(*segment_tasks.values(), return_exceptions=True)

    async def _fetch_segment(self, segment_uri: str):
        """単一セグメントの ChunkedMessage を処理する。"""
        async for cm in self._fetch_protobuf_stream(segment_uri, chat.ChunkedMessage):
            if not self._running:
                break
            try:
                self._process_chunked_message(cm)
            except Exception as e:
                logger.debug(f"{_TAG} メッセージ処理エラー: {e}")

    # ---- ユーティリティ ----

    @staticmethod
    def _set_cookie(session: aiohttp.ClientSession, name: str, value: str):
        """Cookie を .nicovideo.jp ドメインで設定（全サブドメインに送信される）"""
        from http.cookies import SimpleCookie
        c = SimpleCookie()
        c[name] = value
        c[name]["domain"] = ".nicovideo.jp"
        c[name]["path"] = "/"
        session.cookie_jar.update_cookies(c)

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=_HTTP_HEADERS)
            # 保存済み Cookie を復元
            if self._cookies:
                for k, v in self._cookies.items():
                    self._set_cookie(self._session, k, v)
        return self._session

    def stop(self):
        self._running = False

    async def close(self):
        self._running = False
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

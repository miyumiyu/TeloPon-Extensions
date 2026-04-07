"""
ニコニコ生放送 配信者API — アンケート・運営コメント・コメント投稿
認証（user_session Cookie）が必要。
"""

from __future__ import annotations

import aiohttp

import logger

_TAG = "[NicoBroadcaster]"

_API_HEADERS = {
    "content-type": "application/json",
    "origin": "https://live.nicovideo.jp",
    "referer": "https://live.nicovideo.jp/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}


class BroadcasterAPI:
    """配信者向け操作API（要 user_session 認証）"""

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    # ---- アンケート ----

    async def create_enquete(self, program_id: str, question: str, items: list[str]) -> bool:
        """アンケートを作成・開始する"""
        url = f"https://live2.nicovideo.jp/unama/watch/{program_id}/enquete"
        payload = {"question": question, "items": items}
        try:
            async with self._session.post(
                url, json=payload, headers=_API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    logger.info(f"{_TAG} アンケート作成成功")
                    return True
                logger.warning(f"{_TAG} アンケート作成失敗: HTTP {resp.status}")
                return False
        except Exception as e:
            logger.warning(f"{_TAG} アンケート作成エラー: {e}")
            return False

    async def show_enquete_result(self, program_id: str) -> bool:
        """アンケート結果を表示する"""
        url = f"https://live2.nicovideo.jp/unama/watch/{program_id}/enquete/result"
        try:
            async with self._session.post(
                url, headers=_API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    logger.info(f"{_TAG} アンケート結果表示成功")
                    return True
                logger.warning(f"{_TAG} アンケート結果表示失敗: HTTP {resp.status}")
                return False
        except Exception as e:
            logger.warning(f"{_TAG} アンケート結果表示エラー: {e}")
            return False

    async def close_enquete(self, program_id: str) -> bool:
        """アンケートを終了する"""
        url = f"https://live2.nicovideo.jp/unama/watch/{program_id}/enquete"
        try:
            async with self._session.delete(
                url, headers=_API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    logger.info(f"{_TAG} アンケート終了成功")
                    return True
                logger.warning(f"{_TAG} アンケート終了失敗: HTTP {resp.status}")
                return False
        except Exception as e:
            logger.warning(f"{_TAG} アンケート終了エラー: {e}")
            return False

    # ---- 運営コメント ----

    async def send_operator_comment(
        self, program_id: str, text: str, *,
        user_name: str = "", is_permanent: bool = False, color: str = "",
    ) -> bool:
        """運営コメントを投稿する"""
        url = f"https://live2.nicovideo.jp/watch/{program_id}/operator_comment"
        payload: dict = {"text": text, "isPermanent": is_permanent}
        if user_name:
            payload["userName"] = user_name
        if color:
            payload["color"] = color
        try:
            logger.debug(f"{_TAG} 運営コメント送信: url={url} payload={payload}")
            async with self._session.put(
                url, json=payload, headers=_API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                body = await resp.text()
                if resp.status == 200:
                    logger.info(f"{_TAG} 運営コメント投稿成功")
                    return True
                logger.warning(f"{_TAG} 運営コメント投稿失敗: HTTP {resp.status} body={body[:200]}")
                return False
        except Exception as e:
            logger.warning(f"{_TAG} 運営コメント投稿エラー: {e}")
            return False

    async def delete_operator_comment(self, program_id: str) -> bool:
        """運営コメントを削除する"""
        url = f"https://live2.nicovideo.jp/watch/{program_id}/operator_comment"
        try:
            async with self._session.delete(
                url, headers=_API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    logger.info(f"{_TAG} 運営コメント削除成功")
                    return True
                logger.warning(f"{_TAG} 運営コメント削除失敗: HTTP {resp.status}")
                return False
        except Exception as e:
            logger.warning(f"{_TAG} 運営コメント削除エラー: {e}")
            return False

    # ---- 統計情報 (REST) ----

    async def get_statistics(self, program_id: str) -> dict | None:
        """統計情報を取得する（フォールバック用。通常はNDGRのstateで取得）"""
        url = f"https://live2.nicovideo.jp/watch/{program_id}/statistics"
        try:
            async with self._session.get(
                url, headers=_API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception:
            return None

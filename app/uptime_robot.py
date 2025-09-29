import logging
from typing import Dict, Any, Optional, AsyncIterator, Iterable

import aiohttp

from .utils import normalize_domain

log = logging.getLogger("uvicorn.error")


class UptimeRobot:
    BASE_URL = "https://api.uptimerobot.com/v3"

    def __init__(self, token: str, timeout: int = 20, conn_limit: int = 20):
        self.token = token
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector = aiohttp.TCPConnector(limit=conn_limit, ssl=True)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _req(self, method: str, path_or_url: str, **kwargs) -> Dict[str, Any]:
        url = self._normalize_api_url(path_or_url)
        sess = await self._get_session()

        async with sess.request(method, url, **kwargs) as r:
            try:
                data = await r.json()
            except Exception:
                data = {"status": "error", "message": (await r.text())[:1000]}
            data["code"] = r.status
            return data

    @staticmethod
    def _normalize_api_url(path_or_url: str) -> str:
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url.replace("http://", "https://", 1)

        return f"{UptimeRobot.BASE_URL}{path_or_url}"

    async def _iter_monitors(self) -> AsyncIterator[Dict[str, Any]]:
        url_or_path = "/monitors"
        seen = set()

        while True:
            resp = await self._req("GET", url_or_path)
            if resp.get("code") != 200:
                log.warning("GET /monitors failed: %s", resp)
                return

            for m in resp.get("data"):
                yield m

            next_link = resp.get("nextLink")
            if not next_link or next_link in seen:
                return

            seen.add(next_link)
            url_or_path = next_link

    async def find_monitor_by_url(self, url: str) -> Optional[dict]:
        async for m in self._iter_monitors():
            if normalize_domain(m.get("url", "")) == url:
                return m

        return None

    async def create_http_monitor(
            self,
            url: str,
            friendly_name: str,
            interval: int = 300,
            http_method: str = "POST",
            timeout: int = 30,
            grace_period: int = 0,
    ) -> Dict[str, Any]:
        payload = {
            "type": "http",
            "url": url,
            "friendlyName": friendly_name,
            "interval": interval,
            "httpMethodType": http_method.upper(),
            "timeout": timeout,
            "gracePeriod": grace_period,
        }
        return await self._req("POST", "/monitors", json=payload)

import time
from typing import Any

import httpx

from flagswitch_sdk.exceptions import FlagSwitchConnectionError, InvalidApiKeyError


_BASE_URL = "http://localhost:8010/api/fs"
_CACHE_TTL = 30


class FlagSwitch:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._cache_ttl = _CACHE_TTL
        self._cache: dict[str, Any] = {}
        self._cache_ts: float = 0

    def _is_cache_valid(self) -> bool:
        return bool(self._cache) and (time.time() - self._cache_ts) < self._cache_ttl

    async def _fetch_flags(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient() as http:
                response = await http.get(
                    f"{_BASE_URL}/evaluate",
                    headers={"X-Api-Key": self._api_key},
                    timeout=5.0,
                )
        except httpx.RequestError as e:
            raise FlagSwitchConnectionError(f"Failed to reach FlagSwitch server: {e}")

        if response.status_code == 401:
            raise InvalidApiKeyError("Invalid or inactive API key.")

        if response.status_code != 200:
            raise FlagSwitchConnectionError(
                f"Unexpected response from FlagSwitch: {response.status_code}"
            )

        payload = response.json()
        return payload.get("data") or {}

    async def _get_flags(self) -> dict[str, Any]:
        if self._is_cache_valid():
            return self._cache

        flags = await self._fetch_flags()
        self._cache = flags
        self._cache_ts = time.time()
        return flags

    async def is_enabled(self, key: str, default: bool = False) -> bool:
        flags = await self._get_flags()
        return bool(flags.get(key, default))

    async def get_all_flags(self) -> dict[str, Any]:
        return await self._get_flags()

    def invalidate_cache(self) -> None:
        self._cache = {}
        self._cache_ts = 0

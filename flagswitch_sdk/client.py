import time
from typing import Any

import httpx

from flagswitch_sdk.exceptions import FlagSwitchConnectionError


from flagswitch_sdk.helper import (
    _DEFAULT_BASE_URL,
    _DEFAULT_CACHE_TTL,
    _evaluate,
    _handle_response,
)


# ── Async client ───────────────────────────────────────────────────────────────


class FlagSwitch:
    def __init__(
        self,
        api_key: str,
        environment: str,
        base_url: str = _DEFAULT_BASE_URL,
        cache_ttl: int = _DEFAULT_CACHE_TTL,
    ):
        self._api_key = api_key
        self._environment = environment
        self._base_url = base_url.rstrip("/")
        self._cache_ttl = cache_ttl
        self._cache: dict[str, Any] = {}
        self._cache_ts: float = 0

    def _is_cache_valid(self) -> bool:
        return bool(self._cache) and (time.time() - self._cache_ts) < self._cache_ttl

    async def _fetch_flags(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(
                    f"{self._base_url}/evaluate",
                    headers={"X-Api-Key": self._api_key},
                    json={"environment": self._environment},
                    timeout=5.0,
                )
        except httpx.RequestError as e:
            raise FlagSwitchConnectionError(f"Failed to reach FlagSwitch server: {e}")
        return _handle_response(response, self._environment)

    async def _get_raw_flags(self) -> dict[str, Any]:
        if self._is_cache_valid():
            return self._cache
        flags = await self._fetch_flags()
        self._cache = flags
        self._cache_ts = time.time()
        return flags

    async def is_enabled(
        self, key: str, default: bool = False, context: dict = {}
    ) -> bool:
        flags = await self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        return _evaluate(flag, context)["enabled"]

    async def get_variation(
        self, key: str, default: str = "", context: dict = {}
    ) -> str:
        flags = await self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        return _evaluate(flag, context).get("value", default)

    async def get_value(self, key: str, default: Any = None, context: dict = {}) -> Any:
        flags = await self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        return _evaluate(flag, context).get("value", default)

    async def get_string(self, key: str, default: str = "", context: dict = {}) -> str:
        value = await self.get_value(key, default, context)
        try:
            return str(value)
        except (TypeError, ValueError):
            return default

    async def get_number(
        self, key: str, default: float = 0.0, context: dict = {}
    ) -> float:
        value = await self.get_value(key, default, context)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    async def get_json(self, key: str, default: Any = None, context: dict = {}) -> Any:
        flags = await self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        result = _evaluate(flag, context)
        value = result.get("value", default)
        return value if isinstance(value, (dict, list)) else default

    async def get_all_flags(self, context: dict = {}) -> dict[str, Any]:
        flags = await self._get_raw_flags()
        return {key: _evaluate(flag, context) for key, flag in flags.items()}

    def invalidate_cache(self) -> None:
        self._cache = {}
        self._cache_ts = 0


# ── Sync client ────────────────────────────────────────────────────────────────


class FlagSwitchSync:
    def __init__(
        self,
        api_key: str,
        environment: str,
        base_url: str = _DEFAULT_BASE_URL,
        cache_ttl: int = _DEFAULT_CACHE_TTL,
    ):
        self._api_key = api_key
        self._environment = environment
        self._base_url = base_url.rstrip("/")
        self._cache_ttl = cache_ttl
        self._cache: dict[str, Any] = {}
        self._cache_ts: float = 0

    def _is_cache_valid(self) -> bool:
        return bool(self._cache) and (time.time() - self._cache_ts) < self._cache_ttl

    def _fetch_flags(self) -> dict[str, Any]:
        try:
            with httpx.Client() as http:
                response = http.post(
                    f"{self._base_url}/evaluate",
                    headers={"X-Api-Key": self._api_key},
                    json={"environment": self._environment},
                    timeout=5.0,
                )
        except httpx.RequestError as e:
            raise FlagSwitchConnectionError(f"Failed to reach FlagSwitch server: {e}")
        return _handle_response(response, self._environment)

    def _get_raw_flags(self) -> dict[str, Any]:
        if self._is_cache_valid():
            return self._cache
        flags = self._fetch_flags()
        self._cache = flags
        self._cache_ts = time.time()
        return flags

    def is_enabled(self, key: str, default: bool = False, context: dict = {}) -> bool:
        flags = self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        return _evaluate(flag, context)["enabled"]

    def get_variation(self, key: str, default: str = "", context: dict = {}) -> str:
        flags = self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        return _evaluate(flag, context).get("value", default)

    def get_value(self, key: str, default: Any = None, context: dict = {}) -> Any:
        flags = self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        return _evaluate(flag, context).get("value", default)

    def get_string(self, key: str, default: str = "", context: dict = {}) -> str:
        value = self.get_value(key, default, context)
        try:
            return str(value)
        except (TypeError, ValueError):
            return default

    def get_number(self, key: str, default: float = 0.0, context: dict = {}) -> float:
        value = self.get_value(key, default, context)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_json(self, key: str, default: Any = None, context: dict = {}) -> Any:
        flags = self._get_raw_flags()
        flag = flags.get(key)
        if flag is None:
            return default
        result = _evaluate(flag, context)
        value = result.get("value", default)
        return value if isinstance(value, (dict, list)) else default

    def get_all_flags(self, context: dict = {}) -> dict[str, Any]:
        flags = self._get_raw_flags()
        return {key: _evaluate(flag, context) for key, flag in flags.items()}

    def invalidate_cache(self) -> None:
        self._cache = {}
        self._cache_ts = 0

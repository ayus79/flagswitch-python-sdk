import time
from typing import Any

import httpx

from flagswitch_sdk.exceptions import (
    EnvironmentNotFoundError,
    FlagSwitchConnectionError,
    InvalidApiKeyError,
)


_BASE_URL = "http://localhost:8010/api/fs"
_CACHE_TTL = 30


def _handle_response(response: httpx.Response, environment: str) -> dict[str, Any]:
    if response.status_code == 401:
        raise InvalidApiKeyError("Invalid or inactive API key.")
    if response.status_code == 404:
        raise EnvironmentNotFoundError(
            f"Environment '{environment}' not found for this project."
        )
    if response.status_code != 200:
        raise FlagSwitchConnectionError(
            f"Unexpected response from FlagSwitch: {response.status_code}"
        )
    return response.json().get("data") or {}


class FlagSwitch:
    def __init__(self, api_key: str, environment: str):
        self._api_key = api_key
        self._environment = environment
        self._cache: dict[str, Any] = {}
        self._cache_ts: float = 0

    def _is_cache_valid(self) -> bool:
        return bool(self._cache) and (time.time() - self._cache_ts) < _CACHE_TTL

    async def _fetch_flags(self, context: dict) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(
                    f"{_BASE_URL}/evaluate",
                    headers={"X-Api-Key": self._api_key},
                    json={"environment": self._environment, "context": context},
                    timeout=5.0,
                )
        except httpx.RequestError as e:
            raise FlagSwitchConnectionError(f"Failed to reach FlagSwitch server: {e}")
        return _handle_response(response, self._environment)

    async def _get_flags(self, context: dict) -> dict[str, Any]:
        if not context and self._is_cache_valid():
            return self._cache
        flags = await self._fetch_flags(context)
        if not context:
            self._cache = flags
            self._cache_ts = time.time()
        return flags

    async def is_enabled(
        self, key: str, default: bool = False, context: dict = {}
    ) -> bool:
        flags = await self._get_flags(context)
        flag = flags.get(key)
        if flag is None:
            return default
        return bool(flag.get("value", default))

    async def get_variation(
        self, key: str, default: str = "", context: dict = {}
    ) -> str:
        flags = await self._get_flags(context)
        flag = flags.get(key)
        if flag is None:
            return default
        return flag.get("value", default)

    async def get_value(self, key: str, default: Any = None, context: dict = {}) -> Any:
        flags = await self._get_flags(context)
        flag = flags.get(key)
        if flag is None:
            return default
        return flag.get("value", default)

    async def get_all_flags(self, context: dict = {}) -> dict[str, Any]:
        return await self._get_flags(context)

    def invalidate_cache(self) -> None:
        self._cache = {}
        self._cache_ts = 0


class FlagSwitchSync:
    def __init__(self, api_key: str, environment: str):
        self._api_key = api_key
        self._environment = environment
        self._cache: dict[str, Any] = {}
        self._cache_ts: float = 0

    def _is_cache_valid(self) -> bool:
        return bool(self._cache) and (time.time() - self._cache_ts) < _CACHE_TTL

    def _fetch_flags(self, context: dict) -> dict[str, Any]:
        try:
            with httpx.Client() as http:
                response = http.post(
                    f"{_BASE_URL}/evaluate",
                    headers={"X-Api-Key": self._api_key},
                    json={"environment": self._environment, "context": context},
                    timeout=5.0,
                )
        except httpx.RequestError as e:
            raise FlagSwitchConnectionError(f"Failed to reach FlagSwitch server: {e}")
        return _handle_response(response, self._environment)

    def _get_flags(self, context: dict) -> dict[str, Any]:
        if not context and self._is_cache_valid():
            return self._cache
        flags = self._fetch_flags(context)
        if not context:
            self._cache = flags
            self._cache_ts = time.time()
        return flags

    def is_enabled(self, key: str, default: bool = False, context: dict = {}) -> bool:
        flags = self._get_flags(context)
        flag = flags.get(key)
        if flag is None:
            return default
        return bool(flag.get("value", default))

    def get_variation(self, key: str, default: str = "", context: dict = {}) -> str:
        flags = self._get_flags(context)
        flag = flags.get(key)
        if flag is None:
            return default
        return flag.get("value", default)

    def get_value(self, key: str, default: Any = None, context: dict = {}) -> Any:
        flags = self._get_flags(context)
        flag = flags.get(key)
        if flag is None:
            return default
        return flag.get("value", default)

    def get_all_flags(self, context: dict = {}) -> dict[str, Any]:
        return self._get_flags(context)

    def invalidate_cache(self) -> None:
        self._cache = {}
        self._cache_ts = 0

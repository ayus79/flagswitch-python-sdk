import asyncio
from typing import Any

from flagswitch_sdk.flagswitch_core import FlagSwitchCore
from flagswitch_sdk.exceptions import (
    InvalidApiKeyError,
    EnvironmentNotFoundError,
    FlagSwitchConnectionError,
)


def _raise_from_rust(e: RuntimeError) -> None:
    msg = str(e)
    if msg.startswith("INVALID_API_KEY:"):
        raise InvalidApiKeyError(msg.split(":", 1)[1])
    if msg.startswith("ENV_NOT_FOUND:"):
        raise EnvironmentNotFoundError(msg.split(":", 1)[1])
    raise FlagSwitchConnectionError(msg.split(":", 1)[-1])


class FlagSwitch:
    def __init__(self, api_key: str, environment: str):
        self._core = FlagSwitchCore(api_key, environment)

    async def is_enabled(self, key: str, default: bool = False) -> bool:
        try:
            return await asyncio.to_thread(self._core.is_enabled, key, default)
        except RuntimeError as e:
            _raise_from_rust(e)

    async def get_all_flags(self) -> dict[str, Any]:
        try:
            return await asyncio.to_thread(self._core.get_flags)
        except RuntimeError as e:
            _raise_from_rust(e)

    def invalidate_cache(self) -> None:
        self._core.invalidate_cache()


class FlagSwitchSync:
    def __init__(self, api_key: str, environment: str):
        self._core = FlagSwitchCore(api_key, environment)

    def is_enabled(self, key: str, default: bool = False) -> bool:
        try:
            return self._core.is_enabled(key, default)
        except RuntimeError as e:
            _raise_from_rust(e)

    def get_all_flags(self) -> dict[str, Any]:
        try:
            return self._core.get_flags()
        except RuntimeError as e:
            _raise_from_rust(e)

    def invalidate_cache(self) -> None:
        self._core.invalidate_cache()

__version__ = "0.3.0"
__author__ = "FlagSwitch"

from flagswitch_sdk.client import FlagSwitch, FlagSwitchSync
from flagswitch_sdk.exceptions import (
    EnvironmentNotFoundError,
    FlagSwitchConnectionError,
    FlagSwitchError,
    InvalidApiKeyError,
)

__all__ = [
    "FlagSwitch",
    "FlagSwitchSync",
    "FlagSwitchError",
    "InvalidApiKeyError",
    "EnvironmentNotFoundError",
    "FlagSwitchConnectionError",
]

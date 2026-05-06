# FlagSwitch Python SDK

Python SDK for [FlagSwitch] — feature flag management.

## Install

```bash
pip install flagswitch-sdk
```

## Usage

```python
from flagswitch_sdk import FlagSwitch

client = FlagSwitch(api_key="fsXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

# Check if a flag is enabled
enabled = await client.is_enabled("show-new-dashboard")

# With a fallback default
enabled = await client.is_enabled("show-new-dashboard", default=False)

# Get all flags at once
flags = await client.get_all_flags()
# {"show-new-dashboard": True, "dark-mode": False, ...}

# Force a fresh fetch (bypass cache)
client.invalidate_cache()
```

## Caching

Flags are cached for 30 seconds by default to avoid hitting the API on every call. Call `invalidate_cache()` to force a refresh immediately.

## Exceptions

```python
from flagswitch_sdk import FlagSwitch, FlagSwitchError, InvalidApiKeyError, FlagSwitchConnectionError

try:
    enabled = await client.is_enabled("my-flag")
except InvalidApiKeyError:
    # bad or inactive API key
except FlagSwitchConnectionError:
    # network issue or server error
except FlagSwitchError:
    # catch-all for any SDK error
```

## Requirements

- Python 3.11+
- httpx

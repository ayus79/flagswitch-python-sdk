import hashlib
from typing import Any

import httpx

from flagswitch_sdk.exceptions import (
    EnvironmentNotFoundError,
    FlagSwitchConnectionError,
    InvalidApiKeyError,
)


_DEFAULT_BASE_URL = "http://localhost:8010/api/fs"
_DEFAULT_CACHE_TTL = 30


# ── Local evaluation helpers ───────────────────────────────────────────────────


def _get_variation_value(variations: list, key: str) -> Any:
    for v in variations:
        if v.get("key") == key:
            return v.get("value")
    return None


def _matches_rule(rule: dict, context: dict) -> bool:
    attr = rule.get("attribute")
    op = rule.get("operator", "equals")
    expected = rule.get("value")
    actual = context.get(attr)

    if actual is None:
        return False

    str_actual = str(actual)
    str_expected = str(expected)

    if op == "equals":
        return str_actual == str_expected
    if op == "not_equals":
        return str_actual != str_expected
    if op == "contains":
        return str_expected in str_actual
    if op == "starts_with":
        return str_actual.startswith(str_expected)
    if op == "ends_with":
        return str_actual.endswith(str_expected)
    if op == "greater_than":
        try:
            return float(actual) > float(expected)
        except (TypeError, ValueError):
            return False
    if op == "less_than":
        try:
            return float(actual) < float(expected)
        except (TypeError, ValueError):
            return False
    return False


def _in_rollout(flag_key: str, stickiness_val: str, percentage: int) -> bool:
    hash_input = f"{flag_key}:{stickiness_val}".encode()
    hash_int = int(hashlib.md5(hash_input).hexdigest(), 16)
    return (hash_int % 100) < percentage


def _evaluate(flag: dict, context: dict) -> dict:
    """Evaluate a raw flag dict against context. Returns {enabled, value}."""
    flag_type = flag.get("type", "boolean")
    variations = flag.get("variations") or []
    rules = flag.get("rules") or []
    rollout = flag.get("rollout") or {}
    default_key = flag.get("default_variation")
    flag_key = flag.get("key", "")

    if not flag.get("enabled"):
        if flag_type == "boolean":
            return {"enabled": False, "value": False}
        return {
            "enabled": False,
            "value": _get_variation_value(variations, default_key),
        }

    # Rules take priority over rollout
    for rule in rules:
        if _matches_rule(rule, context):
            if flag_type == "boolean":
                return {"enabled": True, "value": True}
            return {
                "enabled": True,
                "value": _get_variation_value(variations, rule.get("variation")),
            }

    # Percentage rollout
    if rollout.get("enabled") and rollout.get("percentage", 0) > 0:
        stickiness_attr = rollout.get("stickiness", "user_id")
        stickiness_val = str(context.get(stickiness_attr, ""))
        if _in_rollout(flag_key, stickiness_val, rollout["percentage"]):
            if flag_type == "boolean":
                return {"enabled": True, "value": True}
            for v in variations:
                if v.get("key") != default_key:
                    return {"enabled": True, "value": v.get("value")}

    # Default
    if flag_type == "boolean":
        return {"enabled": True, "value": True}
    return {"enabled": True, "value": _get_variation_value(variations, default_key)}


# ── HTTP helpers ───────────────────────────────────────────────────────────────


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

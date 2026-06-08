"""CANARYNET - self-hosted canary token network.

Generate decoy artifacts (AWS keys, DNS hostnames, doc/web URLs) that have no
legitimate use. When an attacker touches one, the access shows up in your logs
and CANARYNET flags it. Inspired by thinkst/canarytokens, but fully self-hosted
and standard-library only.
"""
from .core import (
    Token,
    TokenStore,
    Alert,
    new_token,
    scan_logs,
    TOKEN_TYPES,
)

TOOL_NAME = "canarynet"
TOOL_VERSION = "1.0.0"

__all__ = [
    "Token",
    "TokenStore",
    "Alert",
    "new_token",
    "scan_logs",
    "TOKEN_TYPES",
    "TOOL_NAME",
    "TOOL_VERSION",
]

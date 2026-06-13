"""Core engine for CANARYNET canary tokens.

Design
------
A canary token is a unique, never-legitimately-used artifact. CANARYNET embeds a
short opaque *canary id* into each token so a single triggered string can be
mapped back to the token that minted it. Token material is generated with
``secrets`` so ids are unguessable.

Token types
-----------
* aws        - a fake AWS access-key id / secret pair (AKIA... format).
* dns        - a unique subdomain under a base zone; a DNS lookup is the trigger.
* web        - a unique HTTP URL path; a GET is the trigger.
* doc        - a document-embeddable URL (same as web, semantic label differs).

Detection
---------
``scan_logs`` walks arbitrary text (web access logs, DNS query logs, CloudTrail
exports, anything) and matches every minted token's canary id or material. Each
match becomes an :class:`Alert`. No network access is performed anywhere.
"""
from __future__ import annotations

import json
import secrets
import string
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

TOKEN_TYPES = ("aws", "dns", "web", "doc")

_B32 = string.ascii_lowercase + "234567"  # base32-ish, dns/url safe


class CanaryError(Exception):
    """Raised on invalid input or unrecoverable state."""


def _canary_id(n: int = 12) -> str:
    """Unguessable, DNS/URL-safe lowercase id."""
    return "".join(secrets.choice(_B32) for _ in range(n))


def _aws_material() -> dict:
    # Realistic-looking but bogus AWS credentials. AKIA prefix is the public
    # access-key-id form; the secret is 40 base64-ish chars.
    key_id = "AKIA" + "".join(secrets.choice(string.ascii_uppercase + "234567") for _ in range(16))
    secret = "".join(secrets.choice(string.ascii_letters + string.digits + "+/") for _ in range(40))
    return {"access_key_id": key_id, "secret_access_key": secret}


@dataclass
class Token:
    """A single canary token."""

    id: str
    type: str
    label: str
    created: float
    material: dict = field(default_factory=dict)
    triggered: int = 0
    last_seen: float | None = None

    def fingerprints(self) -> list[str]:
        """Strings whose presence in a log means this token was touched."""
        fps = [self.id]
        if self.type == "aws":
            fps.append(self.material.get("access_key_id", ""))
            fps.append(self.material.get("secret_access_key", ""))
        elif self.type == "dns":
            fps.append(self.material.get("hostname", ""))
        elif self.type in ("web", "doc"):
            fps.append(self.material.get("url", ""))
            fps.append(self.material.get("path", ""))
        return [f for f in fps if f]

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Alert:
    """A detected token trigger."""

    token_id: str
    token_type: str
    label: str
    matched: str
    source: str
    line_no: int
    excerpt: str

    def as_dict(self) -> dict:
        return asdict(self)


def new_token(type_: str, label: str, base_domain: str = "canary.example.com",
              base_url: str = "https://canary.example.com") -> Token:
    """Mint a fresh canary token of ``type_``."""
    if type_ not in TOKEN_TYPES:
        raise CanaryError(f"unknown token type {type_!r}; choose from {TOKEN_TYPES}")
    if not label or not label.strip():
        raise CanaryError("label must be a non-empty string")

    cid = _canary_id()
    material: dict = {}
    if type_ == "aws":
        material = _aws_material()
        material["note"] = "DECOY credentials - any use is unauthorized"
    elif type_ == "dns":
        host = f"{cid}.{base_domain.strip('.')}"
        material = {"hostname": host}
    elif type_ in ("web", "doc"):
        path = f"/c/{cid}"
        material = {"path": path, "url": base_url.rstrip('/') + path}

    return Token(
        id=cid,
        type=type_,
        label=label.strip(),
        created=time.time(),
        material=material,
    )


class TokenStore:
    """JSON-file-backed collection of tokens."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.tokens: dict[str, Token] = {}
        if self.path.exists():
            self.load()

    def load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8") or "{}")
        except (json.JSONDecodeError, OSError) as exc:
            raise CanaryError(f"cannot read store {self.path}: {exc}") from exc
        self.tokens = {tid: Token(**td) for tid, td in raw.get("tokens", {}).items()}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "tokens": {t.id: t.as_dict() for t in self.tokens.values()}}
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def add(self, token: Token) -> None:
        self.tokens[token.id] = token

    def get(self, token_id: str) -> Token:
        if token_id not in self.tokens:
            raise CanaryError(f"no token with id {token_id!r}")
        return self.tokens[token_id]

    def list(self) -> list[Token]:
        return sorted(self.tokens.values(), key=lambda t: t.created)

    def remove(self, token_id: str) -> Token:
        if token_id not in self.tokens:
            raise CanaryError(f"no token with id {token_id!r}")
        return self.tokens.pop(token_id)


def _iter_lines(text: str) -> Iterable[tuple[int, str]]:
    for i, line in enumerate(text.splitlines(), start=1):
        yield i, line


def scan_logs(tokens: Iterable[Token], text: str, source: str = "<stdin>") -> list[Alert]:
    """Return one :class:`Alert` per (token, log-line) hit.

    Matching is literal substring search over each token's fingerprints, so it
    works on any log format without parsing. A token may match on multiple
    lines, but overlapping fingerprints of the same token (e.g. a trigger URL
    that embeds the raw token id) collapse to one alert per line, keyed on
    the longest matching fingerprint.
    """
    # Pre-compile a fingerprint -> token map. Longer fingerprints first so a
    # match on the full material is preferred for the excerpt context.
    fp_map: list[tuple[str, Token]] = []
    for tok in tokens:
        for fp in tok.fingerprints():
            fp_map.append((fp, tok))
    fp_map.sort(key=lambda x: len(x[0]), reverse=True)

    alerts: list[Alert] = []
    for line_no, line in _iter_lines(text):
        seen_tokens: set[str] = set()
        for fp, tok in fp_map:
            if tok.id in seen_tokens:
                continue
            idx = line.find(fp)
            if idx == -1:
                continue
            seen_tokens.add(tok.id)
            start = max(0, idx - 24)
            end = min(len(line), idx + len(fp) + 24)
            excerpt = line[start:end].strip()
            alerts.append(Alert(
                token_id=tok.id,
                token_type=tok.type,
                label=tok.label,
                matched=fp,
                source=source,
                line_no=line_no,
                excerpt=excerpt,
            ))
            tok.triggered += 1
            tok.last_seen = time.time()
    return alerts

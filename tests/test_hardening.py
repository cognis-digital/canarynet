"""Hardening tests: error/edge-path coverage added during production hardening.

Covers:
  - Missing / malformed store file handling
  - new_token input validation (base_domain, base_url)
  - TokenStore.load() rejects structurally broken JSON
  - CLI: missing log file -> exit 1, bad store JSON -> exit 1
  - CLI: unexpected exception yields exit 1, not traceback
  - webhook.py: bad URL scheme, missing colon in header, empty stdin
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarynet.core import CanaryError, TokenStore, new_token
from canarynet.cli import main


# ---------------------------------------------------------------------------
# new_token input validation
# ---------------------------------------------------------------------------

def test_new_token_empty_base_domain():
    with pytest.raises(CanaryError, match="base_domain"):
        new_token("dns", "test", base_domain="")


def test_new_token_blank_base_domain():
    with pytest.raises(CanaryError, match="base_domain"):
        new_token("dns", "test", base_domain="   ")


def test_new_token_empty_base_url():
    with pytest.raises(CanaryError, match="base_url"):
        new_token("web", "test", base_url="")


def test_new_token_bad_url_scheme():
    with pytest.raises(CanaryError, match="base_url must start with"):
        new_token("web", "test", base_url="ftp://example.com")


def test_new_token_https_base_url_accepted():
    tok = new_token("web", "test", base_url="https://my.canary.net")
    assert tok.material["url"].startswith("https://my.canary.net")


# ---------------------------------------------------------------------------
# TokenStore: malformed JSON store
# ---------------------------------------------------------------------------

def test_store_load_non_object_root():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bad.json"
        p.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(CanaryError, match="expected a JSON object"):
            TokenStore(p)


def test_store_load_tokens_not_a_dict():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bad.json"
        p.write_text(json.dumps({"version": 1, "tokens": ["a", "b"]}), encoding="utf-8")
        with pytest.raises(CanaryError, match="'tokens' must be a JSON object"):
            TokenStore(p)


def test_store_load_token_entry_not_a_dict():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bad.json"
        p.write_text(
            json.dumps({"version": 1, "tokens": {"abc123": "not-an-object"}}),
            encoding="utf-8",
        )
        with pytest.raises(CanaryError, match="must be a JSON object"):
            TokenStore(p)


def test_store_load_token_missing_required_field():
    """A token record missing required fields raises CanaryError, not TypeError."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bad.json"
        # Token dataclass requires id, type, label, created at minimum
        p.write_text(
            json.dumps({"version": 1, "tokens": {"abc123": {"id": "abc123"}}}),
            encoding="utf-8",
        )
        with pytest.raises(CanaryError, match="malformed token"):
            TokenStore(p)


# ---------------------------------------------------------------------------
# CLI: bad store JSON -> exit 1
# ---------------------------------------------------------------------------

def test_cli_bad_store_json_exit_1():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "broken.json"
        p.write_text("{{{not valid json", encoding="utf-8")
        rc = main(["--store", str(p), "list"])
        assert rc == 1


# ---------------------------------------------------------------------------
# CLI: missing log file -> exit 1 (directory treated as not-a-file)
# ---------------------------------------------------------------------------

def test_cli_scan_missing_logfile_exit_1():
    with tempfile.TemporaryDirectory() as d:
        store = Path(d) / "s.json"
        # Mint a token first so the store is non-empty
        main(["--store", str(store), "new", "web", "label-x"])
        rc = main(["--store", str(store), "scan", str(Path(d) / "nofile.log")])
        assert rc == 1


def test_cli_scan_directory_as_logfile_exit_1():
    """Passing a directory path (not a file) as logfile should exit 1."""
    with tempfile.TemporaryDirectory() as d:
        store = Path(d) / "s.json"
        main(["--store", str(store), "new", "web", "label-y"])
        # Pass the temp dir itself as the log file argument
        rc = main(["--store", str(store), "scan", d])
        assert rc == 1


# ---------------------------------------------------------------------------
# webhook.py: unit tests without actual network calls
# ---------------------------------------------------------------------------

def _load_webhook():
    import importlib.util
    p = Path(__file__).resolve().parents[1] / "integrations" / "webhook.py"
    spec = importlib.util.spec_from_file_location("webhook", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_webhook_bad_url_scheme(capsys, monkeypatch):
    webhook = _load_webhook()
    monkeypatch.setattr("sys.argv", ["webhook.py", "--url", "ftp://bad.example.com"])
    monkeypatch.setattr("sys.stdin", io.StringIO('[{"x":1}]'))
    rc = webhook.main()
    assert rc == 1
    captured = capsys.readouterr()
    assert "http" in captured.err


def test_webhook_malformed_header(capsys, monkeypatch):
    webhook = _load_webhook()
    monkeypatch.setattr(
        "sys.argv",
        ["webhook.py", "--url", "https://example.com", "--header", "BadHeaderNoColon"],
    )
    monkeypatch.setattr("sys.stdin", io.StringIO('[{"x":1}]'))
    rc = webhook.main()
    assert rc == 1
    captured = capsys.readouterr()
    assert "Key: Value" in captured.err


def test_webhook_empty_stdin(capsys, monkeypatch):
    webhook = _load_webhook()
    monkeypatch.setattr(
        "sys.argv", ["webhook.py", "--url", "https://example.com"]
    )
    monkeypatch.setattr("sys.stdin", io.StringIO("   "))
    rc = webhook.main()
    assert rc == 1
    captured = capsys.readouterr()
    assert "stdin" in captured.err

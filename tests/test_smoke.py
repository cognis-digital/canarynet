"""Smoke tests for CANARYNET. No network. Run with: python -m pytest -q

Also runnable directly: python tests/test_smoke.py
"""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarynet import TOOL_NAME, TOOL_VERSION, new_token, scan_logs, TOKEN_TYPES
from canarynet.core import TokenStore, CanaryError
from canarynet.cli import main


def test_metadata():
    assert TOOL_NAME == "canarynet"
    assert TOOL_VERSION.count(".") == 2


def test_mint_all_types_unique():
    ids = set()
    for t in TOKEN_TYPES:
        tok = new_token(t, f"label-{t}")
        assert tok.type == t
        assert tok.id and tok.id not in ids
        ids.add(tok.id)
        assert tok.fingerprints()  # has something to match on
    assert len(ids) == len(TOKEN_TYPES)


def test_aws_material_shape():
    tok = new_token("aws", "k")
    assert tok.material["access_key_id"].startswith("AKIA")
    assert len(tok.material["secret_access_key"]) == 40


def test_invalid_type_and_label():
    try:
        new_token("bogus", "x")
    except CanaryError:
        pass
    else:
        raise AssertionError("expected CanaryError for bad type")
    try:
        new_token("web", "   ")
    except CanaryError:
        pass
    else:
        raise AssertionError("expected CanaryError for empty label")


def test_scan_detects_and_counts():
    tok = new_token("web", "runbook")
    log = f"GET /healthz 200\nGET {tok.material['path']} 200\nGET /favicon 404\n"
    alerts = scan_logs([tok], log, source="unit.log")
    assert len(alerts) == 1
    assert alerts[0].token_id == tok.id
    assert alerts[0].line_no == 2
    assert tok.triggered == 1
    assert tok.last_seen is not None


def test_scan_clean_log_no_alerts():
    tok = new_token("dns", "zone")
    assert scan_logs([tok], "nothing interesting here\n") == []
    assert tok.triggered == 0


def test_store_roundtrip(tmp_path=None):
    import tempfile
    d = Path(tempfile.mkdtemp())
    p = d / "store.json"
    store = TokenStore(p)
    tok = new_token("aws", "billing")
    store.add(tok)
    store.save()
    reloaded = TokenStore(p)
    assert reloaded.get(tok.id).material == tok.material
    assert [t.id for t in reloaded.list()] == [tok.id]
    reloaded.remove(tok.id)
    reloaded.save()
    assert TokenStore(p).list() == []


def test_cli_new_and_scan_exit_codes():
    import tempfile
    d = Path(tempfile.mkdtemp())
    store = str(d / "cli.json")

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["--store", store, "--format", "json", "new", "web", "x"])
    assert rc == 0
    tok = json.loads(buf.getvalue())
    path = tok["material"]["path"]

    # clean log -> exit 0
    clean = d / "clean.log"
    clean.write_text("GET / 200\n")
    assert main(["--store", store, "--format", "json", "scan", str(clean)]) == 0

    # triggered log -> exit 2
    hit = d / "hit.log"
    hit.write_text(f"GET {path} 200\n")
    out = io.StringIO()
    with redirect_stdout(out):
        rc = main(["--store", store, "--format", "json", "scan", str(hit)])
    assert rc == 2
    alerts = json.loads(out.getvalue())
    assert alerts and alerts[0]["token_id"] == tok["id"]

    # missing file -> exit 1
    assert main(["--store", store, "scan", str(d / "nope.log")]) == 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed")

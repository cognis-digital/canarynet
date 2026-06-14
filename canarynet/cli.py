"""Command-line interface for CANARYNET.

Subcommands
-----------
  new    TYPE LABEL        mint a token and persist it
  list                     show all tokens
  show   TOKEN_ID          show one token (full material)
  rm     TOKEN_ID          delete a token
  scan   LOGFILE [LOGFILE] scan log file(s) for triggered tokens

Global flags: --version, --format {table,json}, --store PATH.
Returns 0 on success, 1 on error, 2 (from scan) when alerts are found.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import TOOL_NAME, TOOL_VERSION
from .core import CanaryError, TokenStore, new_token, scan_logs

DEFAULT_STORE = "canarynet_tokens.json"


def _emit(obj, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(obj, indent=2))
        return
    # table
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{k:>16}: {v}")
    elif isinstance(obj, list):
        if not obj:
            print("(none)")
            return
        cols = list(obj[0].keys())
        widths = {c: max(len(c), *(len(str(r.get(c, ''))) for r in obj)) for c in cols}
        print("  ".join(c.upper().ljust(widths[c]) for c in cols))
        print("  ".join("-" * widths[c] for c in cols))
        for r in obj:
            print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))
    else:
        print(obj)


def _token_row(tok) -> dict:
    primary = (
        tok.material.get("access_key_id")
        or tok.material.get("hostname")
        or tok.material.get("url")
        or ""
    )
    return {"id": tok.id, "type": tok.type, "label": tok.label,
            "triggered": tok.triggered, "artifact": primary}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=TOOL_NAME, description="Self-hosted canary token network.")
    p.add_argument("--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}")
    p.add_argument("--format", choices=("table", "json"), default="table")
    p.add_argument("--store", default=DEFAULT_STORE, help="path to token store JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    pn = sub.add_parser("new", help="mint a new canary token")
    pn.add_argument("type", choices=("aws", "dns", "web", "doc"))
    pn.add_argument("label")
    pn.add_argument("--base-domain", default="canary.example.com")
    pn.add_argument("--base-url", default="https://canary.example.com")

    sub.add_parser("list", help="list all tokens")

    ps = sub.add_parser("show", help="show one token with full material")
    ps.add_argument("token_id")

    pr = sub.add_parser("rm", help="delete a token")
    pr.add_argument("token_id")

    pc = sub.add_parser("scan", help="scan log file(s) for triggered tokens")
    pc.add_argument("logfile", nargs="+")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    fmt = args.format

    def _err(msg: str) -> int:
        if fmt == "json":
            print(json.dumps({"error": msg}), file=sys.stderr)
        else:
            print(f"error: {msg}", file=sys.stderr)
        return 1

    try:
        store = TokenStore(args.store)

        if args.cmd == "new":
            tok = new_token(args.type, args.label, args.base_domain, args.base_url)
            store.add(tok)
            store.save()
            _emit(tok.as_dict(), fmt)
            return 0

        if args.cmd == "list":
            _emit([_token_row(t) for t in store.list()], fmt)
            return 0

        if args.cmd == "show":
            _emit(store.get(args.token_id).as_dict(), fmt)
            return 0

        if args.cmd == "rm":
            tok = store.remove(args.token_id)
            store.save()
            _emit({"removed": tok.id, "label": tok.label}, fmt)
            return 0

        if args.cmd == "scan":
            toks = store.list()
            if not toks:
                raise CanaryError("no tokens in store; mint one with `new` first")
            all_alerts = []
            for lf in args.logfile:
                path = Path(lf)
                if not path.is_file():
                    raise CanaryError(f"log file not found: {lf}")
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError as exc:
                    raise CanaryError(f"cannot read log file {lf}: {exc}") from exc
                all_alerts.extend(scan_logs(toks, text, source=str(path)))
            store.save()  # persist triggered counts / last_seen
            _emit([a.as_dict() for a in all_alerts], fmt)
            if all_alerts:
                if fmt == "table":
                    print(f"\n!! {len(all_alerts)} canary trigger(s) detected", file=sys.stderr)
                return 2  # alerts found -> non-zero so CI / cron can react
            return 0

    except CanaryError as exc:
        return _err(str(exc))
    except KeyboardInterrupt:
        return _err("interrupted")
    except Exception as exc:  # noqa: BLE001
        return _err(f"unexpected error: {exc}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

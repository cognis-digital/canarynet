# CANARYNET — Self-hosted canary token network — AWS keys, DNS, docs, web URLs

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> Cognis Open Collaboration License (COCL) v1.0 · domain: `blue-team`

[![install](https://img.shields.io/badge/install-git%2B%20%C2%B7%20pipx%20%C2%B7%20uv-6b46c1.svg)](#install--every-way-every-platform)
[![CI](https://github.com/cognis-digital/canarynet/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/canarynet/actions)
[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE)
[![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

**Self-hosted canary token network — AWS keys, DNS, docs, web URLs.**

*Blue Team / Defense — detection, deception, and monitoring for small teams.*

<!-- cognis:layman:start -->
## What is this?

Canarynet is a security tool that lets you create "canary tokens" — fake but realistic-looking credentials (such as AWS keys, web URLs, and DNS hostnames) that you deliberately plant in your systems or documents. If an attacker finds and uses one of these tokens, canarynet alerts you immediately, giving you an early warning that something is being accessed without authorization. It is designed for security-conscious teams and individuals who want a simple, self-hosted way to detect intrusions before damage is done. You run it from the command line, point it at your log files, and it tells you if any of your planted tokens were ever triggered.
<!-- cognis:layman:end -->

## Why

Security and intelligence teams need self-hosted canary token network — AWS keys, DNS, docs, web URLs without standing up heavyweight infrastructure. `canarynet` is single-purpose, scriptable, CI-friendly, and self-hostable: point it at a target, get prioritized findings in the format your workflow already speaks (table, JSON, SARIF, HTML), and wire it into agents over MCP when you want it autonomous.

<!-- cognis:install:start -->
## Install

`canarynet` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/canarynet/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/canarynet/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/canarynet.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/canarynet.git"  # uv
pip install "git+https://github.com/cognis-digital/canarynet.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/canarynet.git
cd canarynet && pip install .
```

Then run:
```sh
canarynet --help
```
<!-- cognis:install:end -->

## Install

```bash
pip install "git+https://github.com/cognis-digital/canarynet.git"
# or, from this repo:
pip install -e ".[dev]"
```

## Quick start

```bash
canarynet --version
canarynet scan demos/                      # run against the bundled demo
canarynet scan demos/ --format sarif --out r.sarif --fail-on high
canarynet scan demos/ --format html --out report.html
canarynet mcp                              # expose as an MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Each scenario folder includes a `SCENARIO.md` describing the situation and the findings to expect.

- [`demos/01-aws-key-honeytoken-tripped/`](demos/01-aws-key-honeytoken-tripped/SCENARIO.md)
- [`demos/01-basic/`](demos/01-basic/SCENARIO.md)
- [`demos/02-document-canary-tripped/`](demos/02-document-canary-tripped/SCENARIO.md)
- [`demos/03-mixed-status/`](demos/03-mixed-status/SCENARIO.md)

## Output formats

- **Table** (default) — human-readable terminal summary
- **JSON** — machine-readable findings for pipelines
- **SARIF** — drops into GitHub code-scanning / IDE problem panes
- **HTML** — shareable report with severity rollups

## Credits / Built on

Cognis composes and credits the best of open source. This tool builds on / interoperates with:

- [`thinkst/canarytokens`](https://github.com/thinkst/canarytokens) — fork base (Thinkst)
- [`thinkst/opencanary`](https://github.com/thinkst/opencanary) — daemon reference

Missing a credit? Open a PR — see [CONTRIBUTING.md](CONTRIBUTING.md).

## How it fits the Cognis Neural Suite

`canarynet` is one of **52 tools** in the [Cognis Neural Suite](https://github.com/cognis-digital). Every tool ships an MCP server, so [Cognis.Studio](https://cognis.studio) agents can call them as scoped capabilities.

**Sibling tools in `blue-team`:** [`sentrylog`](https://github.com/cognis-digital/sentrylog), [`edrgap`](https://github.com/cognis-digital/edrgap), [`phishforge`](https://github.com/cognis-digital/phishforge), [`sbomgate`](https://github.com/cognis-digital/sbomgate), [`honeytrace`](https://github.com/cognis-digital/honeytrace)

## Architecture & roadmap

- Design notes: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Planned work: [`ROADMAP.md`](ROADMAP.md)

## Contributing

PRs, new detections, and demo scenarios are welcome under the collaboration-pull model. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

<a name="verification"></a>
## Verification

[![tests](https://img.shields.io/badge/tests-8%20passing-2ea44f.svg)](AUDIT.md)

Every push is verified end-to-end. Latest audit (2026-06-12):

```text
tests        : 8 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : C:\Python314\python.exe: No module named https
package      : https
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
C:\Python314\python.exe: No module named https
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `python -m https --help` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>


## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

## Responsible use

This is dual-use security software. Use it only against systems, data, and identities you own or are explicitly authorized in writing to test, and in compliance with applicable law.

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*

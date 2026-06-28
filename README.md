# CANARYNET — Self-hosted canary token network — AWS keys, DNS, docs, web URLs

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> Cognis Open Collaboration License (COCL) v1.0 · domain: `blue-team`

[![PyPI](https://img.shields.io/pypi/v/cognis-canarynet.svg)](https://pypi.org/project/cognis-canarynet/)
[![CI](https://github.com/cognis-digital/canarynet/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/canarynet/actions)
[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE)
[![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

**Self-hosted canary token network — AWS keys, DNS, docs, web URLs.**

*Blue Team / Defense — detection, deception, and monitoring for small teams.*


<!-- cognis:example:start -->
## 🔎 Example output

Real, reproducible output from the tool — runs offline:

```console
$ canarynet-emit --version
canarynet 0.1.0
```

```console
$ canarynet-emit --help
usage: canarynet [-h] [--version] [--format {table,json}] [--store STORE]
                 {new,list,show,rm,scan} ...

Self-hosted canary token network.

positional arguments:
  {new,list,show,rm,scan}
    new                 mint a new canary token
    list                list all tokens
    show                show one token with full material
    rm                  delete a token
    scan                scan log file(s) for triggered tokens

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --format {table,json}
  --store STORE         path to token store JSON
```

> Blocks above are real `canarynet` output — reproduce them from a clone.

**Sample result format** _(illustrative values — run on your own data for real findings):_

```
{
"Findings": [
    {
        "id": "1234567890",
        "title": "Suspicious Activity Detected",
        "description": "Anomalous network traffic detected from IP 192.168.1.100",
        "created_at": "2023-02-20T14:30:00Z",
        "updated_at": "2023-02-20T14:30:00Z",
        "objects": [
            {
                "id": "1234567890-object-1",
                "type": "indicator",
                "name": "Suspicious IP",
                "description": "Anomalous network traffic detected from IP 192.168.1.100"
            }
        ]
    }
]
}
```

<!-- cognis:example:end -->

## Usage — step by step

1. **Install** the `canarynet` command:
   ```bash
   pip install cognis-canarynet   # or: pip install -e .   from this repo
   ```
2. **Mint a token.** `new TYPE LABEL` persists a token to the store (`TYPE` is `aws`, `dns`, `web`, or `doc`); place the artifact somewhere an intruder would find it:
   ```bash
   canarynet new aws "prod-backup-keys"
   canarynet new web "internal-wiki-link" --base-url https://canary.example.com
   ```
3. **Inspect the store** — list all tokens, or show one with its full material:
   ```bash
   canarynet list
   canarynet show <TOKEN_ID>
   ```
4. **Scan logs** for triggered tokens; `scan` exits `2` when any canary fired so cron/CI can react:
   ```bash
   canarynet scan /var/log/auth.log /var/log/nginx/access.log
   ```
5. **Automate detection.** Use `--format json` (and `--store` to pin the token file) for machine output, and key alerting off the exit code:
   ```bash
   canarynet --format json scan /var/log/*.log || echo "CANARY TRIGGERED"; alert.sh
   ```

## Why

Security and intelligence teams need self-hosted canary token network — AWS keys, DNS, docs, web URLs without standing up heavyweight infrastructure. `canarynet` is single-purpose, scriptable, CI-friendly, and self-hostable: point it at a target, get prioritized findings in the format your workflow already speaks (table, JSON, SARIF, HTML), and wire it into agents over MCP when you want it autonomous.

## Install

```bash
pip install cognis-canarynet
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

## Interoperability

`canarynet` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.

## Integrations

Forward `canarynet`'s findings to STIX/MISP/Sigma/Splunk/Elastic/Slack/webhooks via
[`cognis-connect`](https://github.com/cognis-digital/cognis-connect). See **[INTEGRATIONS.md](INTEGRATIONS.md)**.

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

## Responsible use

This is dual-use security software. Use it only against systems, data, and identities you own or are explicitly authorized in writing to test, and in compliance with applicable law.

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*

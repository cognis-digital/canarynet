# Demo 01 - Catch an attacker who looted leaked AWS keys

CANARYNET mints decoy artifacts that have **no legitimate use**. The moment one
shows up in a log, you know someone touched something they shouldn't have.

This demo plants a fake AWS access key and a web bug-URL, then scans a sample
CloudTrail-style access log that contains a usage of the decoy key.

## Run it

```sh
# 1. Mint a decoy AWS key pair (drop it in a fake ~/.aws/credentials, a wiki, etc.)
python -m canarynet --store /tmp/cn.json new aws "prod-billing-readonly"

# 2. Mint a web canary URL (embed it in an internal doc / honeypot page)
python -m canarynet --store /tmp/cn.json new web "internal-runbook-link"

# 3. See everything you've planted
python -m canarynet --store /tmp/cn.json list

# 4. Scan an access log. Use the planted key id from step 1 to build a
#    realistic line, OR just scan the bundled sample which already contains
#    a triggered web path:
python -m canarynet --store /tmp/cn.json --format json scan demos/01-basic/access.log
```

## Expected behavior

* `new` prints the token (for `aws`, the decoy `access_key_id` / `secret_access_key`).
* `scan` prints one JSON alert per matched log line and **exits with code 2**
  when any canary is triggered (exit 0 when clean, exit 1 on error). The `2`
  exit code lets a cron job or CI step fire an incident automatically.
* The matched token's `triggered` counter is incremented and persisted.

## Sample log

`access.log` is a small mixed web/DNS access log. It contains a request to a
canary web path of the form `/c/<id>` so the scan demonstrates a real hit once
you paste in the id minted on your machine. The pre-seeded line
`/c/EXAMPLECANARY` won't match your freshly minted token (ids are random) — swap
in your real id to see the alert, exactly as it would happen in production.

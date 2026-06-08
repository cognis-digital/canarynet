# Scenario: AWS key honeytoken hit from Tor exit + bot

Two AWS canary keys triggered within 3 minutes from different IPs. The keys had been deployed in a deliberately leaked git repo to attract scanners.

## Expected findings

- CN-HIT-001 × 2 (critical)

## Why this matters

Confirmed: someone is actively scanning your public repos for keys. Audit and rotate everything within scope.

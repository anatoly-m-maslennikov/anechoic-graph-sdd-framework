---
atom_family: SPEC
atom_id: AN-S-517
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 13
  updated_at: "2026-11-25T22:04:02.281200+00:00"
---
## Summary

Exclude secrets from production logs

## Claim

### Prose Claim


production logs that can contain credentials **or** secret-bearing payloads.


production logs **must not** contain passwords, API keys, access tokens, session secrets, cookies, private keys, complete credentials, **or** unredacted secret-bearing payloads.

## Details

this is the explicit secret-exposure boundary for production log records.

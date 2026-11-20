---
atom_family: SPEC
atom_id: AN-S-517
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 13
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Exclude secrets from production logs

## Claim

### Prose Claim


production logs that can contain credentials **or** secret-bearing payloads.


production logs **must not** contain passwords, API keys, access tokens, session secrets, cookies, private keys, complete credentials, **or** unredacted secret-bearing payloads.

## Details

this is the explicit secret-exposure boundary for production log records.

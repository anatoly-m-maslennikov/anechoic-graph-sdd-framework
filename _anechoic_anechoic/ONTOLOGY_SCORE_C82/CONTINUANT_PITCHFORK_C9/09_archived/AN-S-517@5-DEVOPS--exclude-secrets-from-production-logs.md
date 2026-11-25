---
atom_family: SPEC
atom_id: AN-S-517
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Exclude secrets from production logs

# Summary

Exclude secrets from production logs

## Scope

production logs that can contain credentials **or** secret-bearing payloads.

## Claim

production logs **must not** contain passwords, API keys, access tokens, session secrets, cookies, private keys, complete credentials, **or** unredacted secret-bearing payloads.

## Details

this is the explicit secret-exposure boundary for production log records.

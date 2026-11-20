---
identity:
  atom_id: AN-S-109
context:
  container:
    component: C20
  tier: 3
  lens: QA
state:
  status: active
  version: 18
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject one invalid Codex plugin package

# Reject one invalid Codex plugin package

## Claim checked

A Codex plugin package **contains** a coherent manifest, contained relative references, **and** matching marketplace entry.

## Test case

Build one package whose manifest names a missing packaged capability.

## Acceptance criteria

Package validation rejects it **before** marketplace publication **or** installation.

## Failure disposition

Stop packaging **and** report the missing **or** inconsistent carrier.

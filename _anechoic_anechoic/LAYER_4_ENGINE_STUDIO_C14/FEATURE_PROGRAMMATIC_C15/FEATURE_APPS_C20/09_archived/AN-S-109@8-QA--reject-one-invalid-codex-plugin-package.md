---
atom_family: SPEC
atom_id: AN-S-109
container:
  component: C20
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 00:51:05 +0400
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

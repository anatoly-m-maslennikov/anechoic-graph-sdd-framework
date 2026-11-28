---
atom_family: SPEC
atom_id: AN-S-5183
container:
  component: C14
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---

## Summary

Limit Engine source comments to consumed directives

## Claim

Engine source and tests must contain no prose comments. Keep comment syntax only when an interpreter, build tool or static analyzer uses it, including shebangs, encoding declarations, type annotations and applicable lint suppressions. An explicit purge must preserve code behavior, string literals, docstrings and required directives.

---
atom_family: SPEC
atom_id: AN-S-1297
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Externalize a large static mapping

# Externalize a large static mapping

## Claim checked

one large reusable static mapping is stored outside a hand-authored Python
module while its loader retains a typed, validated boundary.

## Test case

evaluate one changed Python module containing a static mapping above 20 entries
**or** 25 source lines.

## Acceptance criteria

pass **only** **when** the mapping is moved **to** TOML by default, JSON for a schema **or**
machine-interchange need, **or** YAML for one declared distinct feature; its loader
**must** validate the expected structure **without** changing the mapping's meaning.

## Failure disposition

reject the source-size claim **until** data **and** executable behavior are separated.

## Sources

- [CA-M-419 — Ratchet hand-authored Python source boundaries](../05_method/CA-M-419-PROGRAMMATIC-STANDARD-ENG_POLICY--ratchet-hand-authored-python-source-boundaries.md)
- [Python documentation: `tomllib`](https://docs.python.org/3.14/library/tomllib.html)
- [Python documentation: `json`](https://docs.python.org/3.14/library/json.html)

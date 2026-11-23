---
atom_family: SPEC
atom_id: AN-S-85
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject unadmitted Concern closure application

# Reject unadmitted Concern closure application

## Test case

Given one active Concern ID, terminal disposition, optional active resolver **or** subject IDs, **and** a sealed Initiative action, `CLOSE_ATOM` dry run returns the closure action **without** mutation. Direct `--apply` **without** authorized project-local MCP delegation returns a stable rejection **and** leaves **every** carrier, Journal, index, Git history, **and** runtime file unchanged.

Given the same sealed action through authorized MCP delegation, the Tool invokes **only** the canonical lifecycle operation **and** MCP receives durable `COMMIT_TRIGGER` intake acknowledgement **before** success. The Tool itself does **not** append the Journal, stage files, **or** create a Git commit.

## Sources

- [CA-R-1042 — Coordinate Concern closure intent](../04_requirement/CA-R-1042-CLOSE_ATOM-CORE-REQUIREMENT--coordinate-concern-closure-intent.md)

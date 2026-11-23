---
atom_family: SPEC
atom_id: AN-S-125
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Evaluate one sealed Atom relation rebinding

# Evaluate one sealed Atom relation rebinding

## Test case

Given temporary active Markdown Atom carriers, perform dry runs of sealed requests that rewrite one exact relation target **to** a verified canonical active ID **or** remove one exact target. Repeated requests **must** return byte-identical receipts, preserve filename, body, **and** undeclared frontmatter, advance version once **only** **in** the planned result, **and** report no Journal **or** Git effect.

Verify direct `--apply` is rejected **without** authorized project-local MCP delegation. Verify an authorized MCP delegation replaces **only** the sealed source carrier, returns the deterministic receipt, **and** receives durable `COMMIT_TRIGGER` intake acknowledgement **without** a Journal append, staged file, **or** Git commit. Rejections for inactive source, changed digest, wrong version, unavailable relation, missing old target, repeated old target, **and** invalid new target leave source bytes unchanged.

## Sources

- [CA-R-1049 — Rebind one active Atom relation set](../../../306_FEATURE_TOOL_WORKFLOWS/04_requirement/CA-R-1049-TOOL_WORKFLOWS-STANDARD-REQUIREMENT--rebind-one-active-atom-relation-set.md)

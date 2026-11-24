---
atom_family: SPEC
atom_id: AN-S-1403
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Distinguish one protocol failure from one Tool failure

## Claim

### Prose Claim

MCP returns stable model-readable responses that distinguish a protocol failure from a canonical Tool failure.

## Details

### Test case

Produce one invalid protocol message **and** one valid message whose canonical Tool returns a structured failure.

### Acceptance criteria

the two responses are distinct, retain applicable provenance, **and** expose no internal implementation detail.

### Failure disposition

Reject the result adapter **until** it preserves the required distinction.

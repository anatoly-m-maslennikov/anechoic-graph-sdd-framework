---
identity:
  atom_id: AN-S-1398
context:
  container:
    component: C21
  tier: 3
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Preserve canonical Tool ownership through one MCP call

## Claim

### Prose Claim

MCP delegates a call **without** reimplementing the canonical Tool's decisions **or** lifecycle behavior.

## Details

### Test case

Invoke one exposed Tool with a fixture that would reveal an MCP-side target **or** lifecycle decision.

### Acceptance criteria

**only** the canonical Tool performs that decision **and** MCP returns its resulting structured outcome unchanged.

### Failure disposition

Reject the transport implementation as an unauthorized second operation owner.

---
identity:
  atom_id: AN-S-1402
context:
  container:
    component: C21
  tier: 3
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Redact one secret from an MCP result

## Claim

### Prose Claim

MCP does **not** expose a secret through a projected capability result **or** diagnostic.

## Details

### Test case

Inject one secret-bearing diagnostic value into a Tool result fixture.

### Acceptance criteria

the public MCP representation excludes that value while retaining the classified failure meaning.

### Failure disposition

Stop the affected capability **and** treat the representation as a secret-boundary defect.

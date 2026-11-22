---
atom_family: SPEC
atom_id: AN-S-3189
container:
  component: C61
tier: 2
context:
  lens: QA
relations:
  IS_REFERENCE:
  - AN-S-3187@1-draft
  - AN-S-3188@1-draft
  - AN-T-2953
state:
  status: draft
  version: 1
  updated_at: '2026-11-22T16:44:45.347890+00:00'
---

## Summary

Verify state findings against runtime post-state

## Claim

### Prose Claim

- Compare an Epic lifecycle transition with CPython and a JavaScript state transition with Node. Compare post-state as well as the outcome.
- Check mutation-only, output-only, write-and-restore, and silent paths. Require the ordered effect trace and a concrete input for each dead end.
- Include a permitted private mutation, an aliased write to shared state, and a write through a read-only grant. Verify each source location and state owner.
- Record unsupported constructs and missing comparison evidence as unresolved. Lint blocks only confirmed violations in a language with passing post-state checks.
- Change a checked Module or grant and confirm Workbench, Console, MCP, and lint use refreshed findings.
- Check the same witnessed path through Lean and lint. Verify unavailable tools leave unresolved evidence and do not block lint.

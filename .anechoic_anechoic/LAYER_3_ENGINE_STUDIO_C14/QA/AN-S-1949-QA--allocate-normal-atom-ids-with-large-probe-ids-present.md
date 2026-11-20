---
identity:
  atom_id: AN-S-1949
context:
  container:
    component: C14
  tier: 3
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:56:24.915112+00:00'
---
## Summary

Allocate normal Atom IDs with large probe IDs present

## Claim

### Prose Claim

Verify that new Drafts receive the next in-range ID through both indexed and direct allocation. Include a high-numbered probe, an ordinary Current Atom and an ordinary Archived carrier with leading zeros. The archived number still reserves its place when its body is unloaded. Confirm that the high ID remains selectable by its exact reference and that allocation fails before creating a file when the configured range is exhausted.

---
atom_family: SPEC
atom_id: AN-S-2941
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 16:33:24 +0400
---
## Summary

Define Property-value selection with `:=`

## Claim

### Prose Claim

In a Subject or filtered Node expression in a Formal Claim, `:=` combines allowed-value qualification with selection, as in `Workflow//(.Purpose := Runtime)`. The selected value must satisfy effective admissibility: the OR of applicable HAS_ALLOWED_VALUE alternatives, including inherited alternatives, when present, and the AND of applicable HAS_VALUE_CONSTRAINT restrictions, including inherited restrictions. If no HAS_ALLOWED_VALUE group exists, omit that group (true), so no enumeration restriction is imposed. It is selection syntax, not assignment to an occurrence.

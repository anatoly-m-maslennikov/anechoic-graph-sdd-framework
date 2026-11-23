---
atom_family: SPEC
atom_id: AN-S-2048
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: '2026-11-11T18:56:17+04:00'
---
## Summary

Declare Analysis & Advisory

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: "Analysis and Advisory";

Atom/(.Header.Context.Role := "Analysis and Advisory") >| (Role Order Number == 2);
```

## Semantics

Analysis and Advisory covers analysis reports, rationales and spec proposals. It establishes findings, explanations, comparisons, reasons or proposed changes.

For reading historical Atom carriers, `Analysis & Advisory` is an alias for this same Role. New and updated Atom carriers use the canonical Role value `Analysis and Advisory`.

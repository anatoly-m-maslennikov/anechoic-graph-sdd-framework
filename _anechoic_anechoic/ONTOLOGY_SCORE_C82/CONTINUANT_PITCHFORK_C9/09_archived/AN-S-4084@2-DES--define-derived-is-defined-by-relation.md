---
atom_family: SPEC
atom_id: AN-S-4084
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define Derived IS_DEFINED_BY Relation

## Claim

IS_DEFINED_BY is the derived counterpart of the defining GOVERNS links qualified by the Entity Definition ownership rule. It reuses that main link and its qualification; it adds no independently stored reverse fact.

### Formal claim

```text
CFEL > Relation//IS_DEFINED_BY
```

## Details

The main GOVERNS meaning is defined by CA-R-1199. CA-R-2278 qualifies which GOVERNS links define an Entity. The counterpart references those sources instead of repeating their meanings or constraints; the inverse is derived only from that qualified main link.

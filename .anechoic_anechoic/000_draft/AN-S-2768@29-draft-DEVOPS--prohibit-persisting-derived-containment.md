---
identity:
  atom_id: AN-S-2768
context:
  container:
    component: C00
  tier: 1
  lens: DevOps
state:
  status: draft
  version: 29
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Prohibit Persisting Derived Containment

## Claim

### Prose Claim


`CONTAINS` **and** `IS_CONTAINED_BY` relations derived from canonical Carrier nesting.


`CONTAINS` **and** `IS_CONTAINED_BY` relations derived from canonical Carrier nesting **must not** be persisted as independent relation declarations.

## Details

This prohibition applies when canonical Carrier nesting already owns a non-Atom containment fact. An Atom stores its own container in `Header.Container`; its logical parent is not inferred from a directory. For non-Atom facts, this does not ban an independently authored direct `IS_CONTAINED_BY` whose authority is the child's admitted Relation declaration rather than nesting. Do not maintain two independent sources for the same fact. `CONTAINS` remains a derived inverse and is not independently authored.

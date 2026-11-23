---
atom_family: SPEC
atom_id: AN-S-2697
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define Relation

## Claim

Relation defines the structure of reusable Relation Types. A named instance
such as `Relation//RECORDS` or `Relation//IS_EXECUTION_OF` is a reusable Type
that can connect many endpoint pairs. A Type has a canonical Name and Meaning;
its direction, derived inverse, and transitivity meaning describe the Type,
not one actual edge.

An actual directed connection is the tuple (source, Relation Type, target).
Source Reference and Target Reference belong to that connection, not to the
reusable Type. Persist each direct fact once; a declared inverse is derived.
Endpoint permissions, structural constraints, and counts belong in governing
Entity Definitions rather than being inferred from a Type name.

### Formal claim

```text
Relation.Name[string]{1}
Relation.Meaning[string]{1}
```

## Semantics

RECORDS can be reused for different Event Record/occurrence pairs. Defining a
named Type neither creates an actual run, record, or edge nor requires a
separate Relation ID or primary branch.

## Details

Named Type Definition authority is `R/Type: Relation Definition`. The general
`((RELATION_TYPE))` notation remains available where no short operator exists.
No short notation is invented by this Definition.

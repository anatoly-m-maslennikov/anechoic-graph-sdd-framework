---
atom_family: SPEC
atom_id: AN-S-4311
container:
  component: C15
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Declare Query Processing Aspect

## Claim

### Prose Claim

Query Processing is an Engineering Aspect within Data Handling.

### Formal Claim

```CFEL
# model
ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing;
```

## Semantics

Execution of accepted queries and transformations of their materialized results, including paging, filtering, ordering and grouping. Query authoring governs how query text is written; Source Retrieval governs how input files are read.

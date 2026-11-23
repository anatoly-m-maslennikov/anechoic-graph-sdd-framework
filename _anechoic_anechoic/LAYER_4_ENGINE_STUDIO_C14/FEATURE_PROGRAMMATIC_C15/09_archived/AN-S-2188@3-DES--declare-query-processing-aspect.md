---
atom_family: SPEC
atom_id: AN-S-2188
container:
  component: C15
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-11T16:56:16+04:00'
---

## Summary

Declare Query Processing Aspect

## Claim

### Prose Claim

Query Processing is an Engineering Aspect within Data Handling.

### Formal Claim

```CFEL
# project_structure
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing;

(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing) ((INSTANCE_OF)) Aspect;
```

## Semantics

Execution of accepted queries and transformations of their materialized results, including paging, filtering, ordering and grouping. Query authoring governs how query text is written; Source Retrieval governs how input files are read.

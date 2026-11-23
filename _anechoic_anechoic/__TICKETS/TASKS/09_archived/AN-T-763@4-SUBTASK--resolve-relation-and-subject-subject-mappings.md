---
atom_family: TKT
atom_id: AN-T-763
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 06:12:15 +0400
---
## Summary

Resolve relation and subject Subject mappings

# Summary

Resolve relation and subject Subject mappings

## Objective

Refresh the relations_subjects Candidate #7 mapping lane from the live worklist and return complete, source-backed dispositions.

## Details

Read the fresh relations_subjects lane from .anechoic_anechoic/_projection/core-entity-review/presentation/candidate-7.remaining-subject-worklist.json. Keep Graph/Relation definitions separate from Graph/Rule constraints and keep Subject links separate from ordinary Atom relations. Preserve direct relation direction, derive inverses, and treat containment as IS_CONTAINED_BY on the child with CONTAINS derived. Map only from current source meaning, preserving endpoint qualifiers and current Atom ID targets. Return unresolved cases explicitly. Apply no source, content, code, schema, MCP, test, Settings or runtime change.

### Definition of Done

Not Done if the fresh lane is absent/stale, assigned whole-owner or occurrence coverage is incomplete, a meaning is guessed, qualifiers or provenance are lost, unresolved rows are hidden, or any source effect or migration completion is claimed.

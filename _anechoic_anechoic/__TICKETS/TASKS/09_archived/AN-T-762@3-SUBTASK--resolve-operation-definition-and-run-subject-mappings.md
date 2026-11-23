---
atom_family: TKT
atom_id: AN-T-762
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 06:04:11 +0400
---
## Summary

Resolve operation definition and run Subject mappings

# Summary

Resolve operation definition and run Subject mappings

## Objective

Refresh the operations Candidate #7 mapping lane from the live worklist and return complete, source-backed dispositions.

## Details

Read the fresh operations lane from .anechoic_anechoic/_projection/core-entity-review/presentation/candidate-7.remaining-subject-worklist.json. Distinguish operation definitions and named instances from actual Runs/events: definitions may use the Candidate #7 kind-to-instance boundary, while actual runs/events are Occurrents and their records belong to History. Preserve exact names, qualifiers and source identity; do not add an Invocation/Tool Call root or infer runtime behavior. Return every lane row with evidence or unresolved status. Apply no source, content, code, schema, MCP, test, Settings or runtime change.

### Definition of Done

Not Done if the fresh lane is absent/stale, assigned whole-owner or occurrence coverage is incomplete, a meaning is guessed, qualifiers or provenance are lost, unresolved rows are hidden, or any source effect or migration completion is claimed.

---
atom_family: TKT
atom_id: AN-T-1452
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 07:52:46 +0400
---
## Summary

Expose direct Subject lookup through MCP

# Summary

Expose direct Subject lookup through MCP

## Objective

Extend the existing ATOM_SEARCH provider with the accepted closed request/result and root-bound read-only adapter. Use normal registry discovery and applicable source pins. Do not create Session, Run, Journal, staging or authorization records.

## Details

Prepare fixtures independently; production edits require the accepted CA-P-2374 rule packet, and final protocol execution requires the ready CA-P-2375/2376 implementation. These are stage-specific gates, not a whole-Task start BLOCKS relation or an Artifact depends_on relation.

Estimated own work: up to 15 minutes; split before exceeding this bound. Follow the independently reviewed lookup-exposure proposal. Root owns integration and Git. Preserve unrelated changes. Core Subject migration, ordinary content migration, broader connector rebuilding and live publication remain outside this Task.

### Acceptance — 2026-10-14

Independent provider review passed after restoring existing Project boundary/provenance checks before and after lookup. Eight dedicated provider tests are included in the 71 passing ATOM_SEARCH tests. The descriptor is registered through the existing registry, with closed logical inputs/results, actual source pins and no Session/Run/Journal. Existing readers retain their Session behavior: 55 affected tests passed after pin-only refresh.

Implementation: commit `2a40cb4c8`. [Local completion receipt](../../../_projection/core-entity-review/stage2/tools-first/direct-subject-lookup-local-completion.md). No Core Subject migration or ordinary content update was performed.

### Definition of Done

Provider/registry tests pass for the accepted schema, actual source hashes, empty and refusal outcomes; Session behavior is preserved. Installed activation remains separate.


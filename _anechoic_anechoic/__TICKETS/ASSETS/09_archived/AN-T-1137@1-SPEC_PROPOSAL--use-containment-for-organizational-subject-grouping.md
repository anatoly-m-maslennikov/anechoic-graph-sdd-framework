---
atom_family: TKT
atom_id: AN-T-1137
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 02:55:02 +0400
---
## Summary

Use containment for organizational Subject grouping

# Summary

Use containment for organizational Subject grouping

## Operator decision

“Project Model > Actor, etc, not "/"”

“Project Model CONTAINS Actor, etc”

## Meaning

Use the existing CONTAINS relation and its `>` notation for organizational Subject membership. Such containment does not imply broader-to-narrower classification or property inheritance. Keep `/` for real broader-to-narrower classification and preserve legitimate inheritance there. The existing direct IS_CONTAINED_BY / derived CONTAINS convention remains unchanged.

Project Model remains a vocabulary grouping. Its containment of the Actor Subject does not duplicate an Actor, create a Scope Unit ownership claim, or merge an occurrence with its record.

## Review disposition

This selects the semantic correction for SG3-I02 / SG3-F02. The affected path inventory and source migration still need review. Other FPF findings and the distinction between Aspect subtopics, classifications and part structures remain separate.

## Preparation

Successor Drafts are prepared for R2209, R1931, R2150 and R2222. Current sources and generated Projections are unchanged; no renderer, Tool, MCP or runtime code is changed. This file records the decision; Draft preparation is not promotion or migration.

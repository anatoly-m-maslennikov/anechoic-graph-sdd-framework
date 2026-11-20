---
identity:
  atom_id: AN-T-9
context:
  container:
    component: C00
  tier: 3
  template: task
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Migrate Project Scope Unit Graph Generator

# Migrate Project Scope Unit Graph Generator

**when** CA-P-930 is Done, **then** the Assignee **must** make the canonical Project Scope Unit Graph generator derive Scope Unit nodes and parent edges from the current typed relational folder hierarchy.

## Scope

`((GENERATE_PROJECT_GRAPH_STATE Tool source and tests) union (current Scope Unit and Epic Directory Carrier naming authority) union (the canonical Local Configuration Project Configuration Carrier) union (.anechoic_anechoic typed relational folders))`

## Definition of Done

the Task is **not done if** (the generator requires retired `.anechoic`, retired `002_FRAMEWORK_ENGINE`, **or** root Project Configuration paths **or** treats a Job as a Scope Unit registry **or** treats an Epic Directory as a Scope Unit **or** omits a canonical typed Scope Unit Directory **or** derives parentage from anything other than the nearest typed Scope Unit ancestor **or** emits uppercase `ANECHOIC` as the Project identity **or** an identical source frontier produces different output **or** tests fail).

## Details

identify Scope Unit folders through current Directory Carrier grammar. use folder Type to distinguish Scope Units from Epics. use Jobs only as work Claims that may govern Scope Units **or** Epics.

## Completion Evidence

The generator now discovers 13 active typed Scope Unit Directory Carriers under `.anechoic_anechoic`, derives each parent edge from its nearest typed Scope Unit ancestor, and excludes Epic and inactive lifecycle carriers. It derives actual Structural Level from typed Scope Unit ancestor depth, allocates the numeric-prefix Structural Level width dynamically from the greatest current level, and emits the remaining digits as Navigational Order Number; Layer Local Order remains separate. It follows the current one-hyphen Epic Directory Carrier grammar, binds the nested Local Configuration Project Configuration carrier at revision 4, emits lowercase `anechoic` Project identity, and does not write registered Projections. Six focused tests pass; full execution evidence is stored in `execution_evidence/CA-P-931-project-scope-unit-graph-generator-migration.projection.json`.

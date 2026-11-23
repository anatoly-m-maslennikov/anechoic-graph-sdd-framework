---
atom_family: TKT
atom_id: AN-T-3293
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 07:12:55 +0400
---
## Summary

Produce Complete Methodology Conflict Report

# Produce Complete Methodology Conflict Report

**when** CA-P-920 is Done, **then** the Assignee **must** derive one complete deterministic conflict report from the exact normalized Core Meta-Model **and** Local Configuration source frontier.

## Scope

`((the exact active RMEDO Atom revisions in CORE_META_MODEL) union (the exact active RMEDO Atom revisions in LOCAL_CONFIGURATION) union (the empty non-contributing INSTALLED_EXTENSIONS Scope Unit) union (the GENERATE_ENTITY_GRAPH result for Core Meta-Model plus Local Configuration) union (the COMPILE_APPLICABLE_METHODOLOGY dry-run result))`

## Definition of Done

the Task is **not done if** (the report lacks its exact source-frontier digest **or** omits a duplicate governed-Term Definition, duplicate selected Atom identity, unresolved replacement, incompatible retained Candidate, unresolved priority, output-path collision, Term-system violation, prohibited role-specific Type Term, **or** invalid dependency cycle **or** one conflict lacks **all** exact candidate Carrier paths **and** one stable conflict identity **or** the report silently selects, rewrites, archives, **or** rejects source authority **or** an unresolved conflict produces **or** replaces Applicable Methodology output **or** an identical source frontier produces a different report).

## Details

report conflicts **without** resolving them. distinguish a source-authority defect that requires an Atom repair from a layer-selection conflict that **may** use a digest-bound approval Carrier. include the current `public-interface` duplicate Definition **if** it still exists **in** the normalized frontier.

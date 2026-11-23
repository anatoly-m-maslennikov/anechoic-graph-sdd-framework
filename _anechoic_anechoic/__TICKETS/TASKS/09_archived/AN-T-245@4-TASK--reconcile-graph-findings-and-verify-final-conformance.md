---
atom_family: TKT
atom_id: AN-T-245
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 06:12:13 +0400
---
## Summary

Reconcile graph findings and verify final conformance

# Summary

Reconcile graph findings and verify final conformance

## Claim

the AI Agent **must** resolve the Entities Graph **and** Terms Graph findings for the Project **and** methodology corpus **and** establish a reproducible final result consistent with the repaired source Atoms.

## Definition of Done

the Plan is **not** Done **if** a graph finding remains unresolved, **or** graph repairs introduce a carrier **or** semantic failure, **or** either Projection is stale against the final sources, **or** repeat generation from identical inputs changes governed content, **or** a source Atom is absent from the final coverage accounting.

## Details

- verify **every** Applicable Methodology projected Atom Carrier retains the CA-D-305 one-way relative binding **to** its original methodology-source Atom **and** matches the selected source Revision. rebuild stale projected copies from sources; a missing **or** broken binding blocks completion.
- run both generators from CA-P-1110 against Core Meta-Model alone, combined methodology sources, **and** the Project corpus with its applicable methodology.
- examine gaps, unresolved Terms/Entities, duplicate definitions, unexpected isolated nodes, conflicting typed Relations, missing source references, **and** prohibited cycles under their actual graph-specific rules.
- repair defects **in** their authoritative sources **or** faulty generator Implementation; do **not** repair a generated graph as a separate source of truth. a legitimate isolated node **or** cross-scope reference is **not** automatically a defect.
- rerun mechanical validation **and** semantic review for **all** affected Atoms **and** neighbors, then regenerate both graphs; add regression tests for generator corrections.
- refresh affected derived outputs, including Applicable Methodology **when** its source inputs changed, **without** overwriting unresolved conflict decisions.
- record final source revisions, tool/prompt versions, commands, coverage counts, findings/dispositions, test results, **and** deterministic rebuild evidence. timestamp differences alone do **not** imply changed graph content.
- apply current source authority, including CA-R-1598 **and** CA-D-478–483; do **not** treat an outdated compiled copy as newer authority.
- check Project Principles **before** escalating uncertainty; ask the Operator **if** confidence remains **<99%**. do **not** silently weaken an Evaluation **or** discard a finding **to** pass.
- preserve unrelated work **and** history; follow the current revision, replacement, Summary identity, **and** approval rules.

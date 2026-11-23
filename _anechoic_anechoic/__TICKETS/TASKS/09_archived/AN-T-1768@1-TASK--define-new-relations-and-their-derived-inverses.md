---
atom_family: TKT
atom_id: AN-T-1768
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 20:00:14 +0400
---
## Summary

Define new Relations and their derived inverses

# Summary

Define new Relations and their derived inverses

## Objective

Define new Relations and their derived inverses.

## Details

After CA-P-2685, CA-P-2686.

Prepare Definition Atoms for the missing Relations, including IS_EXECUTION_OF, RECORDS and EXECUTES where those exact meanings remain supported. Specify direct meaning, both endpoint kinds, applicable cardinalities and the derived inverse meaning/name. Do not infer a type, inverse name or permission merely from its spelling.

Workflow Run executes one Workflow definition; Event Records describe occurrences/runs while Journal contains the records; the live Runtime executes work, not the Engineering topic or stored engine Code. Keep definitions, actual occurrences and records distinct. Bind existing short forms to their correct declared directions without introducing a backwards operator.

Apply endpoint and other valid-structure constraints inside the relevant Definition Claim. Do not create R/Type: Graph Rule instances or replace them with a new Rule population. Examples do not count as registered Relations until their defining sources are ready.

## Definition of Done

The named and short-form Relations have complete Definition Drafts, exact direct/derived directions, endpoint constraints and examples that preserve the approved meanings.

## Progress

Not started. Prior analysis and Drafts are inputs, not completion evidence.

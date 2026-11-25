---
atom_family: SPEC
atom_id: AN-S-2354
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: "active"
  version: 12
  updated_at: "2026-11-25T21:03:30.414106+00:00"
---
## Summary

Bind selected Run identities, revisions and lineage

## Scope

Actual Run provenance produced through shared RUN_SUPPORT for the selected
scope. Definition Atoms and their execution records remain distinct.

## Claim

### Prose Claim

RUN_SUPPORT **must** retain distinct actual Workflow Run, Step Run, and Action
Run identities with their exact admitted definition bindings and actual
lineage in the canonical Events Journal.

## Details

- A Workflow Run records its Workflow definition and the ordered admitted
  Workflow graph, Step definitions, and Action definitions with exact Atom
  IDs, Versions, paths, and sealed digests. A Step Run records its exact Step
  definition and its real parent Workflow Run. An Action Run records its exact
  Action definition and its real parent Step/Workflow Run when one exists.
- A standalone actual Action Run has its own Action Run identity and no
  fictitious Workflow Run or Step Run. Nested invocations record only their
  actual parent Run/Step and any actual predecessor/successor Run relation;
  ending a predecessor never starts, approves, or completes a successor.
- The stable action identity, Run identity, definition identity, event
  identity, and Initiative identity have different meanings and must not be
  collapsed. Repeated report delivery, recovery, or Tool transport does not
  manufacture another Run identity.
- Completed effects retain their original bindings and lineage. Revalidation
  of remaining work may record a new decision but must not rewrite history,
  reset retry allowance, or replay a completed effect.
- Projection Action Runs additionally retain target Projection, exact selected
  source Atom revisions and Journal selection, generator/configuration
  reference, and produced revision only when it exists, as required by
  AN-S-1479.

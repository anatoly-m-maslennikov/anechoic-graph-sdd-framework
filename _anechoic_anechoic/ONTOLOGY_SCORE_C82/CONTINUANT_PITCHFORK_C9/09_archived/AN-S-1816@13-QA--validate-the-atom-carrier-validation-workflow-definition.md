---
atom_family: SPEC
atom_id: AN-S-1816
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Validate the Atom Carrier Validation Workflow definition

# Summary

Validate the Atom Carrier Validation Workflow definition

## Scope

the Atom Carrier Validation Workflow definition.

## Claim

the Atom Carrier Validation definition check **must** reject a graph **or** binding that cannot preserve its declared read-only assessment boundary.

- require **=1** entry **and** **=1** Step node, a resolvable Step reference, **=1** Action per Step, explicit compatible input bindings, **and** admitted Workflow-scoped transitions.
- require reachable terminal outcomes for incomplete, invalid, valid, **and** execution-error cases as defined by the referenced Action; **none** of the outcomes **may** be silently mapped **to** valid.
- verify that this graph is acyclic, contains no implicit retry **or** repair, **and** does **not** duplicate Action behavior inside its Step bindings **or** graph.
- verify that findings do **not** prevent assessment of independent targets, while missing authority **or** changed inputs cannot become proof of conformance.
- reference current self-sufficiency **and** source-binding Evaluations for the checked conditions; definition conformance **must not** be reported as a successful Tool execution.

## Details

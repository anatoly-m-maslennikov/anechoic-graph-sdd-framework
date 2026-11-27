---
atom_family: SPEC
atom_id: AN-S-2350
concern:
  subject: "Carrier"
  path: "Model"
  relation: "is_contained_by"
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 19
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Implement Atom Carrier Validation **in** VALIDATE_ATOMS

## Scope

the `VALIDATE_ATOMS` Tool's implementation of the Check Atoms methodology Action.

## Claim

### Prose Claim

the `VALIDATE_ATOMS` Tool **must** implement **=1** methodology Action, Check Atoms under CA-O-087-CORE_META_MODEL-ACTION--check-atoms.

- that Action is the sole authority for operational behavior, selection, findings, **and** result meanings; the Tool's RMED specifies its Implementation **without** copying that authority.
- a Workflow invokes the Action through a Step; the Tool does **not** implement **or** own the Workflow graph **or** impose a Workflow on direct Action calls.
- return the Action's results faithfully, including failed **and** incomplete assessments; do **not** add repair, promotion, archive, **or** semantic-review behavior.
- this binding follows CA-R-1516-PROJECT_CONFIGURATION-REQUIREMENT--bind-each-tool-to-one-methodology-action **and** CA-R-1517-PROJECT_CONFIGURATION-RULE--keep-tool-operational-authority-outside-its-own-subtree. this binding **must not** declare a new Scope Unit **or** require a particular Workflow **to** build the Tool.
- supported mechanical coverage **must** include the current Content Role-specific body Property contracts. Effective Plan Assignee resolution is deferred. distinguish an implemented check blocked by unavailable context from a deferred implementation; neither outcome establishes conformance.

## Details

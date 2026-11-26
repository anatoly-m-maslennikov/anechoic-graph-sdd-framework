---
atom_family: SPEC
atom_id: AN-S-1614
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 27
  updated_at: "2026-11-25T23:09:44.066888+00:00"
---
## Summary

Require conforming Workflow execution

## Claim

### Prose Claim


Workflow execution.


an executor of a Workflow **must** conform **to** the applicable methodology execution rules rather than inventing behavior that is absent from its governing definitions.

## Details

- resolve the Workflow, referenced Actions and called Workflows, Step bindings, declared Step structure, terminal outcomes, **and** applicable execution rules **before** their use. bind definition Revisions **and** revalidate definition changes under AN-S-1617 rather than silently resolving a different Revision during the same Run.
- preserve supplied inputs, returned results, **and** actual Run identities as declared by AN-S-1709 and recorded under AN-S-1617.
- admit work **only** within the applicable authorization, Operator-approval, retry, waiting, **and** recovery conditions. a missing capability **or** unresolved rule blocks the affected execution rather than granting permission. a well-formed definition remains valid **when** a selected executor lacks a required capability; definition validation **and** execution admission are distinct checks.
- a Workflow **may** assume these declared capabilities; it **must not** require a particular executor product merely **to** define its behavior.

this conformance boundary does **not** select a server, programming language, storage technology, **or** a Workflow for building the executor itself.

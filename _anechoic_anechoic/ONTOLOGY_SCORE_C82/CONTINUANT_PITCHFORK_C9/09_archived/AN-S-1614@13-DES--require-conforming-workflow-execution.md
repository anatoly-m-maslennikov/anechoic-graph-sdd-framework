---
atom_family: SPEC
atom_id: AN-S-1614
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Require conforming Workflow execution

# Summary

Require conforming Workflow execution

## Scope

Workflow execution.

## Claim

an executor of a Workflow **must** conform **to** the applicable methodology execution rules rather than inventing behavior that is absent from its governing definitions.

## Details

- resolve the Workflow, referenced Actions, Step bindings, typed transitions, terminal outcomes, **and** applicable execution rules **before** their use. bind definition Revisions **and** revalidate definition changes under CA-R-1525 rather than silently resolving a different Revision during the same Run.
- preserve supplied inputs, returned results, **and** actual Run identities under CA-R-1509, CA-R-1510, **and** CA-R-1511.
- admit work **only** within the applicable authorization, Operator-approval, retry, waiting, **and** recovery conditions. a missing capability **or** unresolved rule blocks the affected execution rather than granting permission. a well-formed definition remains valid **when** a selected executor lacks a required capability; definition validation **and** execution admission are distinct checks.
- a Workflow **may** assume these declared capabilities; it **must not** require a particular executor product merely **to** define its behavior.

this conformance boundary does **not** select a server, programming language, storage technology, **or** a Workflow for building the executor itself.

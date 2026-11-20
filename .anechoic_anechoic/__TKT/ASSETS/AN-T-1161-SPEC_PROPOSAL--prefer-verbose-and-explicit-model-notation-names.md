---
atom_family: TKT
atom_id: AN-T-1161
structure:
  container:
    component: C00
  priority: 2
context:
  template: Spec Proposal
state:
  status: active
  version: 2
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Prefer verbose and explicit Model-notation names

## Decision

Use verbose, self-describing names and explicit structure in Model-notation and operation proposals. Optimize for making the meaning clear at the point of use rather than minimizing characters. Prefer execute_selection() over the tentative materialize() name because it states which operation is performed.

Name the intended operation and result clearly. Do not rely on an unexplained abbreviation or an implicit property projection to save characters. Existing accepted operators and names are not automatically renamed by this style decision; any concrete change belongs in its own proposal or Draft.

## State

The style applies to subsequent proposal writing. CA-A-1288 records the concrete Selection-execution name. This record does not promote the deferred function language or change Current methodology, tools or runtime.

---
atom_family: TKT
atom_id: AN-T-2029
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: archived
  version: 3
  updated_at: 2026-11-11 08:59:06 +0400
---

## Summary

Admit the Atom Lifecycle Tool contract

## Concern

Which operations and invalid-input behavior should the new MCP Tools expose under P2934? Current O127 admits seven operations in one Workflow, including Move. It waits for an additional input dictionary on a format or allowed-value error and allows cancellation while waiting. The six separate Workflow drafts remain unadopted and omit Move.

## Details

Select the Current combined operation contract or review and adopt the split contracts with a disposition for Move. Decide how a new Tool obtains corrected input when no generic Workflow engine is in scope. The retained MCP provider has transport cancellation but no lifecycle input continuation. An immediate invalid-input result would change the Current waiting behavior.

The retirement removed the old lifecycle effect adapters. Retained metadata, Header, scope and Journal primitives can support new effects. Direct Update of an exactly selected carrier has Current requirements for persisted readback, unchanged ID, Version and Updated At, and preservation of omitted properties. Current R1093, M374 and D623 require every changed same-ID edit to advance Version and Updated At and retain history. O128, R1432, R1788 and E521 require Direct Update to preserve those values. Before implementing a persisted Direct Update, decide which rule governs and reconcile the affected sources. The exact old/new scalar patch shape is already available in R1934 and D623. Prepare disposable fixtures while this decision is open.

The installed Codex App Server relays standard MCP forms in the same Tool call. The no-effect probe delivered corrected input on Accept and kept the Action counter at zero on Cancel. See CA-P-2967. Decide the response for clients without form support and verify the real Tool's cancellation boundary before publishing it.

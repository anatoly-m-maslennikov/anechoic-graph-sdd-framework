---
atom_family: SPEC
atom_id: AN-S-1661
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 35
  updated_at: 2026-10-29 07:17:18 +0400
---
## Summary

Use one Project Journal for governed provenance

# Summary

Use one Project Journal for governed provenance

## Scope

ANECHOIC-governed provenance events in a Project.

## Claim

**every** Project **must** use **`=1`** authoritative Work Journal for **all** ANECHOIC-governed provenance events, including Artifact changes, Workflow Runs, Step Runs, Action executions, **and** Implementation lifecycle events. append supplied actual observations to that Project Journal and read them as recorded. each explicit append is an append, including repeated data; no canonical-once, deduplication, prior-history, chain, validation, receipt, retry or recovery prerequisite applies.

Existing Journal entries remain unchanged and readable without migration or synthetic baselines. The Journal is a log of supplied observations, not permission or proof of source, lifecycle, Run or Git correctness; it does not promise historical replay or recovery. its logical event table does **not** require **`=1`** physical file **or** a database table; Carrier representation remains governed by Delivery authority.

## Details

Runtime technical and business Journals may preserve their own operational histories in configured local or remote sinks. They are not additional Project Work Journals. Preserve actually supplied references without inventing canonical bindings. Distinct operational observations remain distinct facts under CA-R-1470; the Project Journal imposes no cross-log reconciliation or recording gate.

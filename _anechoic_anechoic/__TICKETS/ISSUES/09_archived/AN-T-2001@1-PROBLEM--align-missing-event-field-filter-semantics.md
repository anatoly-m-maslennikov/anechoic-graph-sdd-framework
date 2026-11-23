---
atom_family: TKT
atom_id: AN-T-2001
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-10-05 01:45:00 +0400
---
## Summary

Align missing Event field filter semantics

# Summary

Align missing Event field filter semantics

## Concern

CA-R-1869 version 2 rejected an absent Event pointer locally, conflicting with
CA-R-1850's shared comparison rule that an absent selector compares false and
that explicit `null` remains a value.

## Resolution

CA-R-1869 version 3 limits local rejection to selector namespace, RFC6901
escaping or syntax, and dot-qualified traversal. A syntactically valid Event
pointer absent from an individual Event now reaches CA-R-1850 unchanged.
CA-E-575 version 3 records the explicit missing-versus-null fixture. This
resolves only the source conflict; it makes no runtime implementation claim.

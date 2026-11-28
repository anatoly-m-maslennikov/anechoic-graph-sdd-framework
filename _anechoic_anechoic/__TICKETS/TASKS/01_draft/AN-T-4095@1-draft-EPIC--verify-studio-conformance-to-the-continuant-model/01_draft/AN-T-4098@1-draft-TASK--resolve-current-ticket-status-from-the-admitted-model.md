---
atom_family: TKT
atom_id: AN-T-4098
container:
  atom: AN-T-4095
priority: 2
context:
  template: task
  label: Task
state:
  status: draft
  version: 1
  updated_at: '2026-11-28T09:00:23.658085+00:00'
---

## Summary

Resolve Current Ticket Status from the admitted Model

## Finding

The C30 fallback domain includes Ticket Status `active`. The current
admitted Ticket Status domain excludes it. Both can be reproduced
with the Status domain reader.

## Acceptance

Derive the effective Ticket Status domain from the admitted Model.
Verify that a Project-specific Status declaration affects the real
consumer. Keep legacy carrier compatibility explicit and preserve
the archive evidence.

## Implementation

A current Model must declare its scoped Status domains. Carrier capture
uses those domains and rejects a Ticket Status absent from its Model.
The older bootstrap packet and unbound compatibility capture keep
their existing fallback. The focused suite verified legacy bootstrap
and a Project-specific Status through the Ticket lifecycle.

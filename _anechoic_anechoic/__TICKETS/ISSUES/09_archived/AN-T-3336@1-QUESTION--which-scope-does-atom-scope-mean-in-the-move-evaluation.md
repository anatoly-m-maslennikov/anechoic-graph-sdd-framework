---
atom_family: TKT
atom_id: AN-T-3336
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-10-24 11:17:52 +0400
---
## Summary

Which scope does Atom/Scope mean in the MOVE evaluation?

# Summary

Which scope does Atom/Scope mean in the MOVE evaluation?

## Question

Does the legacy Atom/Scope dependency in CA-E-172 mean local placement, a
target Scope Unit, or Substance Scope?

## Scope

The one legacy Subject dependency in Current CA-E-172. This is not a general
scope-model redesign or permission to migrate existing Concerns.

## Details

Bounded choice: use Atom.Local Scope Unit. The MOVE fixture explicitly stays
within the same owning Scope Unit, preserves content and identity, and excludes
ownership transfer. It names Claim Scope separately. This supports local
placement without inventing a fourth Scope property or treating applicability
as ownership. Keep its complete body, fixture, relations and Status unchanged.

This records the remaining interpretation uncertainty for the later content
review under CA-P-1970; it does not change the test behavior or claim that the
fixture has run. No general Atom/Scope alias follows from this local choice.

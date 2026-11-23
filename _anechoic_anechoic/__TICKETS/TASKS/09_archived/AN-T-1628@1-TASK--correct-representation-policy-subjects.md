---
atom_family: TKT
atom_id: AN-T-1628
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-26 05:17:30 +0400
---
## Summary

Correct representation-policy Subjects

# Summary

Correct representation-policy Subjects

## Objective

Correct I02's source relationship errors using the Operator's existing rule:
a D Atom governs the thing/property whose representation it specifies.

## Details

Estimated own work: up to 15 minutes. Follow the accepted root definitions.

- Read Current D651/D652 and D525. The audit's Versions are source leads,
  not execution pins.
- For numeric Tier representation, use the existing canonical Atom.Tier
  Subject; preserve filename applicability in Content Scope or the Claim.
  Do not make Atom a narrower kind of Filename.
- Map D525's persistent-state Carrier reference to the existing canonical
  Carrier Subject, not to a subtype of an Occurrent Runtime. Preserve the
  actual technical-runtime and persistent-state distinction.
- Use the already-defined full paths and operator meanings. Do not invent
  a new Carrier entity for each represented property.
- Preserve the represented obligations, unchanged source content and existing
  history. Record normal Current-update predecessors and readback evidence.
- Ask only if a concrete source cannot be mapped without a new meaning.

## Definition of Done

- The affected Subjects express the intended subtype/property relationships.
- No source in this batch makes Atom a Filename kind or a persistent Carrier
  a Runtime kind.
- The original representation obligations and applicability are preserved.
- No new Domain entity, renderer code or general content migration was added.

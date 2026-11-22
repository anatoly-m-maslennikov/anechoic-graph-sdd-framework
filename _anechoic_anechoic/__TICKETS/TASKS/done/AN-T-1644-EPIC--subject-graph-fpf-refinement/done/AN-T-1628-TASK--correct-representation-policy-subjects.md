---
atom_family: TKT
atom_id: AN-T-1628
container:
  atom: AN-T-1644
priority: 2
context:
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-10-26 06:39:23 +0400
---
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

### Completion evidence

D651/D652 govern Atom.Tier; D525 governs the actual Carrier rather than a Runtime subtype. V11 PASS.

Source verification: `.anechoic_tmp/subject-fpf-refinement/verify.final.md`.
Final source/output pins: `.anechoic_tmp/subject-fpf-refinement/graph-closure/graph.subject-views.manifest.json`.
Actual effect verified; no production tool/runtime implementation or release is claimed.

## Definition of Done

- The affected Subjects express the intended subtype/property relationships.
- No source in this batch makes Atom a Filename kind or a persistent Carrier
  a Runtime kind.
- The original representation obligations and applicability are preserved.
- No new Domain entity, renderer code or general content migration was added.

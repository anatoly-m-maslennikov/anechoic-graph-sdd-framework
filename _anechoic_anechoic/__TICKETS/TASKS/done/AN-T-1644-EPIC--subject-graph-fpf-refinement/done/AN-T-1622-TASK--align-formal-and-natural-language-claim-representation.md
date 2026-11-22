---
atom_family: TKT
atom_id: AN-T-1622
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

Align formal and natural-language Claim representation

## Objective

Align the affected authoring and Delivery contracts with P2642 and decision
D04, without changing tool or renderer implementation.

## Details

Run after P2642. Estimated own work: up to 15 minutes.

- Read Current R1997/D637's formal Graph Rule representation clauses and
  R2150/M232/D653's relevant property/projection contract clauses.
- Separate Claim meaning from its carrier. Natural-language Claim uses
  atom.content.claim; structured formal Claim may use atom.claim.*.
  Governing Configuration remains another admitted form for formal statements.
- Correct only clauses that incorrectly require a Markdown Claim or infer
  absence of Claim from absence of that section. Do not prescribe one universal
  Claim location or mechanically move every operative YAML field.
- Retain the actual meanings and structure of existing rules unless a concrete
  accepted correction requires change. Updating retired selector addresses is
  I04, not implicit permission to redesign constraints here.
- Do not make Semantics presence an automatic Atom/config classifier and do
  not convert existing Graph Rule Atoms into Governing Configuration.
- Preserve existing history and create normal predecessors for changed Current
  contracts. Record bounded readback evidence and concrete further work.

No runtime, renderer code, schema engine, Terms Graph or general content
migration is included. The later projection rebuild must follow actual source
corrections, not this Task's creation.

### Completion evidence

D637@18, R2150@5, M232@25, D653@7, M394@16, D479@20 and R1995@10 align actual representation; formal statements are not duplicated into Markdown. V04/V05 PASS.

Source verification: `.anechoic_tmp/subject-fpf-refinement/verify.final.md`.
Final source/output pins: `.anechoic_tmp/subject-fpf-refinement/graph-closure/graph.subject-views.manifest.json`.
Actual effect verified; no production tool/runtime implementation or release is claimed.

## Definition of Done

- The touched contracts accept the intended natural-language and structured
  formal Claim forms without a duplicate Markdown Claim.
- The projection contract distinguishes logical Claim from its representation,
  rather than treating structured YAML as Claim absence.
- No universal carrier location or unapproved Atom/config conversion is imposed.
- Affected source changes and their predecessors are recorded; no implementation
  or projection rebuild is falsely reported.

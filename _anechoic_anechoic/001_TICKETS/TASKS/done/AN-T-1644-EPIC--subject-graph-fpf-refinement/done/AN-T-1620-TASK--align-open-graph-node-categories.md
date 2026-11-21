---
atom_family: TKT
atom_id: AN-T-1620
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

Align open Graph Node categories

## Objective

Align the governing Graph Node definitions with Operator decision D02:
a Graph Node can be Continuant, Occurrent or Aspect, and the list is open
under the framework's expandability principle.

## Details

Addresses the category part of I01. Estimated own work: up to 15 minutes.

- Read Current R1994 and R2006 after P2640's accepted Subject distinction.
  R1994@8 and R2006@7 are review leads, not fixed execution pins.
- Remove the exhaustive Continuant-or-Occurrent restriction. Admit Aspect
  without closing the list to those three categories.
- Preserve the existing distinction between modeled Domain work and technical
  Engineering runtime. Do not infer a different temporal category from Content
  Role or the owning Scope Unit.
- Do not add unrequested categories or force current abstract topics into a
  new Aspect path. Ask only if a concrete source contradiction requires a
  further Operator decision.
- Preserve useful existing meanings, unrelated sources and existing history.
  Changed Current definitions receive normal predecessor archives.
- Record the actual changed source IDs/versions and bounded readback evidence.
  No renderer, code, MCP, Terms Graph or runtime work is included.

### Completion evidence

R1994@9 and R2006@8 admit open Continuant/Occurrent/Aspect categories. V03 PASS.

Source verification: `.anechoic_tmp/subject-fpf-refinement/verify.final.md`.
Final source/output pins: `.anechoic_tmp/subject-fpf-refinement/graph-closure/graph.subject-views.manifest.json`.
Actual effect verified; no production tool/runtime implementation or release is claimed.

## Definition of Done

- The touched definitions no longer require every Graph Node to be Continuant
  or Occurrent.
- Continuant, Occurrent and Aspect are admitted examples of an open category
  system, not an exhaustive enum.
- Existing Subject branches and Domain/Engineering distinctions are preserved
  unless an explicit accepted correction requires otherwise.
- The changed definitions agree with D01 and D02; no unapproved new Domain
  entity, category or mass Subject remapping was introduced.

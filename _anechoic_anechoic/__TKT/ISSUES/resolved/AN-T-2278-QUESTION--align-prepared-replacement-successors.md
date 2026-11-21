---
atom_family: TKT
atom_id: AN-T-2278
structure:
  container:
    component: C16
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Align prepared replacement successors

## Concern

Replace authority says successors must already be Active on input, while the intended admitted Replace creates complete proposed successors and activates them before archival.

## Evidences

the final source-to-code review confirmed this bounded discrepancy. independent adjudication separated it from unsupported status-transition and authorization-model proposals. focused fixture results establish repair behavior, not actual release completion.

## Blast radius

the affected selected capability and its current release candidate. installed N, historical Events and frozen test snapshots remain preserved.

## Decision

clarify source authority to admit only the sealed complete prepared-new successor set, with all resulting successors Active before predecessor archival; keep the Operator's single Replace boundary.

## Result

R1041 v8 and O128 v4 retain exact predecessor bytes and admit only complete sealed prepared-new successor sets. the actual registered pin refresh is recorded. the replacement suite passes 22 cases, explicitly proving all successors Active before archival, exact destination-collision refusal and distinct used-ID/unused-destination atom-id-collision refusal without effects. independent review accepts this packet; no release success is implied.

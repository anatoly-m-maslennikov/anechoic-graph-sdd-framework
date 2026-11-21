---
atom_family: TKT
atom_id: AN-T-102
container:
  component: C00
priority: 2
context:
  template: Spec Proposal
state:
  status: complete
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Require Journal containment for Event Records

## Decision

The Operator specified History/Journal > Event Record and that Event Record exists only in Journal. Declare the Event Record kind there, not as a standalone Continuant child. Preserve its Continuant classification through /@(Event Record); that reference grants no independent existence. A Journal contains the record, not the actual Event or Run it describes.

The accepted declaration convention requires a permitted Journal container when no standalone option exists. This decision names the required container kind; it does not select an exact numerical upper bound on Journal parents or invent an Event Record identifier.

## Drafts

The new Event Record Definition Draft supplies the previously missing defining source. CA-A-1239 is the primary/property review view. No Current source or actual Journal is changed.

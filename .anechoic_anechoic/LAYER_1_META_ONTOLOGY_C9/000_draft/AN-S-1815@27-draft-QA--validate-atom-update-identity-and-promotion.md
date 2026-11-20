---
atom_family: SPEC
atom_id: AN-S-1815
structure:
  container:
    component: C9
  tier: 4
context:
  lens: QA
state:
  status: draft
  version: 27
  updated_at: '2026-11-13T08:50:15.928174+00:00'
---
## Summary

Validate Atom update identity and promotion

## Claim

### Prose Claim

This Evaluation checks the identity and Version consequences of preparing and promoting an Atom Draft under CA-O-067, CA-O-10016, CA-O-10018, CA-O-10024 and CA-R-1432. An identity observation is read-only and is not a semantic assessment gate or a prerequisite to a lifecycle effect.

## Details

- Supply Draft Versions 1 and 2 for an Atom ID with no published Version. Promote Draft Version 1. Verify Version 1 is Current and Draft Version 2 is byte-for-byte unchanged.
- Supply a Current Atom and a proposal with unchanged Summary and Content Role. Create its Draft and verify the same identity and an unused Version. With Current Version 7, selected Draft Version 6, and another Draft at Version 8, promote the selected Draft and verify that Version 9 is Current, Version 7 is Archived, and the other Draft remains at Version 8.
- Change the Summary while preserving Content Role, and separately change Content Role while preserving Summary. For each case verify promotion produces a new identity at Version 1. Verify the persisted successor matches the supplied properties and the predecessor is archived when named as a replacement target.
- Invoke CA-O-067 as a read-only observation for unchanged and changed Summary and Content Role. Verify it reports the identity fact without persisting an effect, choosing a continuation, or authorizing or blocking the caller's operation.
- Verify a Current Update follows create Draft, archive Current, and promote with the captured Current Status. Generic promotion accepts a supplied allowed Current Status. Verify there is no classification or reassessment gate, retry, or terminal handoff requirement.
- Compare actual source and successor readback to the requested properties, identity and Version. Report an effect failure and actual partial effects explicitly; a Journal recording failure alone does not invalidate a verified effect.

These are evaluation expectations, not evidence that an operation has run.

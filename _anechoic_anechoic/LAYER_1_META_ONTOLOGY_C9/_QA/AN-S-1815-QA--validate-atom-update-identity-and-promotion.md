---
atom_family: SPEC
atom_id: AN-S-1815
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: active
  version: 26
  updated_at: 2026-11-11 14:09:10 +0400
---
## Summary

Validate Atom update identity and promotion

## Claim

### Prose Claim

This Evaluation checks the identity and Version consequences of preparing and promoting an Atom Draft under CA-O-067, CA-O-10016, CA-O-10018, CA-O-10024 and CA-R-1432. An identity observation is read-only and is not a semantic assessment gate or a prerequisite to a lifecycle effect.

## Details

- Supply a Current Atom and a proposal with unchanged Summary and Content Role. Create its Draft and verify the same identity and Version N+1; promote it and verify that Version is retained without another increment.
- Change the Summary while preserving Content Role, and separately change Content Role while preserving Summary. For each case verify promotion produces a new identity at Version 1. Verify the persisted successor matches the supplied properties and the predecessor is archived when named as a replacement target.
- Invoke CA-O-067 as a read-only observation for unchanged and changed Summary and Content Role. Verify it reports the identity fact without persisting an effect, choosing a continuation, or authorizing or blocking the caller's operation.
- Verify a Current Update follows create Draft, archive Current, and promote with the captured Current Status. Generic promotion accepts a supplied allowed Current Status. Verify there is no classification or reassessment gate, retry, or terminal handoff requirement.
- Compare actual source and successor readback to the requested properties, identity and Version. Report an effect failure and actual partial effects explicitly; a Journal recording failure alone does not invalidate a verified effect.

These are evaluation expectations, not evidence that an operation has run.

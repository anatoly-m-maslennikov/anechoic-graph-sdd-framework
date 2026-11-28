---
atom_family: SPEC
atom_id: AN-S-1846
container:
  component: C58
tier: 3
context:
  template: action
  lens: DOM/MTD
state:
  status: active
  version: 6
  updated_at: '2026-11-28T09:21:26.937336+00:00'
---
## Summary

Promote one Atom Draft

## Claim scope

This Action advances one selected non-container Atom revision under its
applicable Model. For SPEC, a Draft becomes Ready and a Ready revision
becomes Active.

## Claim

When finalizing a SPEC Draft as Ready, keep each Active predecessor.

At SPEC activation, resolve the Active predecessor of the same Atom ID,
if present. Resolve different predecessor Atoms by stable ID through
`IS_REPLACEMENT_FOR`. Archive each eligible Active predecessor once.
Keep links to already Archived predecessors. Report a missing or
ambiguous target before applying effects.

For other Atom families, apply the allowed Current Status and archive
eligible Current replacement targets at publication.

Preserve the Version of each archived target. Set Updated At when
changing its Status. Retain the selected revision's Version. If the
Summary or Content Role changes from its source, use a new identity
at Version 1. Derive the filename and location from the Model.
Remove the carrier consumed by the transition.

On an effect failure, stop and report completed and incomplete effects.
A Journal observation of a completed replacement identifies the
predecessor and published successor. Record it separately from the
source effects.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

The saved revision and its Status, any archived replacement targets,
and the removed source carrier. A waiting result requests additional
input. A failure identifies incomplete effects. Report any Journal
warning separately.

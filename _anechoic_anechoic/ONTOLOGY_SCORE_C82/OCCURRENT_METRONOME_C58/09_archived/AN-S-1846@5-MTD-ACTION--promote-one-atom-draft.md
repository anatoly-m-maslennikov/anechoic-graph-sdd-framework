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
  status: archived
  version: 5
  updated_at: '2026-11-28T09:21:26.937336+00:00'
---
## Summary

Promote one Atom Draft

## Claim scope

This Action publishes one exact selected Draft for one non-container Atom under the applicable model. Replacement targets explicitly named by the Draft are archived as part of promotion.

## Claim

For a Draft of a new Version of the same Atom, include its exact same-ID predecessor. A Draft names each different predecessor under `IS_REPLACEMENT_FOR` by stable Atom ID. Each newly linked predecessor must be Ready or Active. Resolve each identity once. Before publishing the Draft as Current, archive each eligible Current target once. When revising a successor, preserve its links to already Archived predecessors. Preserve the Version of each archived target. Set Updated At when changing its Status. Then publish the Draft using the supplied allowed Current Status, set its Updated At to the Status change time, and remove its Draft carrier. If Summary or Content Role changed from its source, promote a new identity at Version 1; otherwise retain the existing Draft Version without an additional increment. Derive the filename and location from the model. On an effect failure stop and report completed and incomplete effects. A Journal observation of completed replacement identifies the predecessor and published successor. Record it independently of the source effects.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

`savedCurrentAtom`, archived replacement targets and `removedDraft`, a request for additional input, or an explicit failure; any Journal warning is separate.

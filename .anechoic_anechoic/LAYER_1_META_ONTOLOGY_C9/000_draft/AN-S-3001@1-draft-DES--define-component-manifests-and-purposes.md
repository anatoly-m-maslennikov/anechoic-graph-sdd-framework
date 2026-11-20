---
identity:
  atom_id: AN-S-3001
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:02:57.528847+00:00'
---
## Summary

Define Component Manifests and Purposes

## Claim

### Prose Claim

A Component Manifest is a Tier 0 Spec Atom declaring the described child Component’s existence, stable ID, name, parent, and layer where applicable. Its settings resolve from that Manifest. A Component Purpose is a Tier 0 Spec Atom stating why the child exists, with responsibilities and obligations in its details. A child can start with a Manifest and add one Purpose later. The parent Component contains both in its own Component Spec Section; each identifies the child it describes. A local extension defining a new Component kind belongs in PMETA.

## Details

Acceptance: a Manifest-only child is valid; a Purpose and Manifest for a child reside in the parent Spec Section and identify that child.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.

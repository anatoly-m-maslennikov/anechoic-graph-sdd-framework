---
atom_family: SPEC
atom_id: AN-S-2180
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-20T11:23:31.865565+00:00'
---

## Summary

Declare Atom.Header.Container

## Claim

### Prose Claim

The native carrier stores the Atom’s immediate Container in `context.container`.

The mapping has exactly one key. `component` names a Component by its stable ID. `atom` names an Atom by its stable ID and selects its Current revision. The Container is explicit. Resolve the containing Component through that chain. Reject missing targets and containment cycles.

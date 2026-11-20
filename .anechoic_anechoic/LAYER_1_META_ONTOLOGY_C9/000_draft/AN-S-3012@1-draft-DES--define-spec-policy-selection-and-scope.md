---
identity:
  atom_id: AN-S-3012
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:04.589666+00:00'
---
## Summary

Define Spec Policy selection and scope

## Claim

### Prose Claim

A Spec Policy directly affects Specification: it applies to matching Spec Atoms selected by its explicit `affects` property in its own Component and the full descendant Component tree. A filter may use criteria including Lens, Tier, Template, a Concern Path subtree, or logical Component name. `component.name` identifies the Component containing the selected Atom. For a child's Purpose and Manifest that is the parent Component. A parent Policy may constrain `io_allowance` on child Component Manifests it contains. An Atom may be affected by several Policies and Solutions; actors resolve conflicting claims as other Specification conflicts.

## Details

Acceptance: a Policy owned by A can select a matching Atom in descendant C, but not a matching Atom in a sibling outside A's tree. A Policy in parent A selecting `component.name: A` can match its contained Manifest describing child B; selecting B by that criterion does not match that Manifest. Multiple matching Policies remain applicable; selection alone establishes no extra precedence.

Sources: CA-A-1462@1-draft, CA-P-3082@1. Task: CA-P-3082.

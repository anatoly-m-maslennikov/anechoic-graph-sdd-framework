---
atom_family: SPEC
atom_id: AN-S-3014
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: "2026-11-23T01:48:06.190382+00:00"
---
## Summary

Bind Spec Atoms to existing Realization with trace sidecars

## Claim

### Prose Claim

Keep `<package>__spec_bind.yaml` at the root of the existing Realization Package. Use its full directory name. Use `implements` and `applies` for exact Atom revision pins. Omit empty keys. An `implements` pin gives `IMPLEMENTS` from Realization to Spec and `IS_IMPLEMENTED_BY` in reverse. Applied Standards cover the Component and its descendants. Resolve paths from the selected Project root.

Keep tests in the Package's direct `<package>__tests/` child. Derive `TESTS` from that child to the Package and `IS_TESTED_BY` in reverse, with or without a Spec Binding. A sibling or deeper match supplies no edge.

Classify files under the Test Package's `assets/` as test assets, including code used as input. Classify recognized source outside `assets/` as test code. Total tests are the sum. Leave files without a declared classification out of the split.

A passing mapped check supports the behavior it exercises. The pinned Spec defines that behavior.

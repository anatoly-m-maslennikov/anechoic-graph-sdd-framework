---
atom_family: SPEC
atom_id: AN-S-3192
container:
  component: C16
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-21T17:37:22.737472+00:00'
---

## Summary

Derive exact Atom revision references

## Guarantee

Given an Atom ID, a version and a Status from an admitted Atom, derive the
exact reference as `<atom-id>@<version>`. Append `-draft` when the Status is
Draft. Return the derived value without writing the Atom.

## References

AN-S-2066, AN-S-3056, and AN-T-2947.

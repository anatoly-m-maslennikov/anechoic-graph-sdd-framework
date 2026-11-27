---
atom_family: SPEC
atom_id: AN-S-3388
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-26T16:38:46.226190+00:00'
---

## Summary

Verify one selected Python algorithm in Lean

## Claim

### Prose Claim

After the State Analyzer comparison, use PastaLean to translate one
bounded Python algorithm. Start with transitive dependency selection
for a rebuild. Pin the source, translation, and one property from the
algorithm's Spec.

Validate supported translations with independent evidence, including a
CPython comparison. Use ProgLib where it can validate the translation.
Check the property in Lean and record a proof or a concrete
counterexample. Keep unsupported constructs and open proof obligations
unresolved.

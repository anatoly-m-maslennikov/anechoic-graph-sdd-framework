---
atom_family: SPEC
atom_id: AN-S-4735
container:
  component: C14
tier: 1
context:
  template: POLICY
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-23T18:03:30.250723+00:00'

---

## Summary

Analyze the full checkout before release

## Claim

### Prose Claim

#### Full-checkout scope

The Static phase covers the full Engine checkout from the locked Engine
development environment with its declared tooling available. Its selection
is checkout-wide, not changed-Package selection.

#### Static work and evidence

Run each source analyzer once and run the Static analyzer tests. Include the
declared source-quality, ownership, and boundary checks. Record analyzer
diagnostics and test results without mutating source.

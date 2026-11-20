---
atom_family: SPEC
atom_id: AN-S-2291
structure:
  container:
    component: C50
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-13T17:18:13.986621+00:00'
---
## Summary

Verify the generated Model build and instance validation

## Claim

### Prose Claim

1. Build the selected ANECHOIC Model. Import the generated package and verify that a narrower class inherits its declared base. Verify that package contents follow CA-R-3136.
2. Build with a missing parent, an inheritance cycle, an unresolved Relation endpoint, and an invalid Python Claim. Each case reports an error to stderr and stops the build.
3. At the instance write boundary, accept a valid proposed instance. Reject an undeclared Property, incorrect value type, inadmissible value, and a cardinality or Relation violation before writing.
4. Submit a batch with a valid target followed by an invalid target and another valid target. Verify the first write remains applied, the error is reported to stderr, and processing stops at the invalid target.

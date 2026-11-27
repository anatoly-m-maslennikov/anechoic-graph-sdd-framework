---
atom_family: SPEC
atom_id: AN-S-3391
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:27.892604+00:00"
---
## Summary

Declare Architecture Analysis

## Purpose

Measure the size of code and the Spec it realizes. Use ownership and dependency evidence to help maintainers review Package boundaries.

Delegate measuring code and Spec and reviewing Package boundaries to Code and Spec Metrics. Delegate checking implementation behavior against its formal Spec to Implementation Verification.

This Component delegates implementation to its child Components.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C73',
    name='Architecture Analysis',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}}
```

## Component Contract

### Measure code and Spec and explain Package review candidates

#### Guarantee

For an admitted Project snapshot, provide read-only Component and Package measurements with their populations, units, and ownership. Show the reasons and supporting evidence for each Package review candidate. Keep the published Spec-to-Realization measurements available.

Delegate checking implementation behavior against its formal Spec to Implementation Verification. Preserve source evidence and report unresolved coverage.

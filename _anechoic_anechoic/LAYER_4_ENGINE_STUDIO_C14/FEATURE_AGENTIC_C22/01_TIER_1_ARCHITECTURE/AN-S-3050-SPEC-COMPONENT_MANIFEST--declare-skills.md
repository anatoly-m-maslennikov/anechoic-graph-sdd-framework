---
atom_family: SPEC
atom_id: AN-S-3050
container:
  component: C22
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:29.862349+00:00"
---

## Summary

Declare SKILLS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C23',
    name='SKILLS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []}, 'exports': {}},
 'state': {'reads': [], 'writes': []}}
```

## Boundary scope

This definition covers the ane skill carrier. It provides instructions for a consumer; it performs no MCP calls or state effects.

## Component Contract

### Guide anechoic mcp use

#### Guarantee

Guide an agent to use the host-configured ANECHOIC MCP with the explicit Project root and verify the result.

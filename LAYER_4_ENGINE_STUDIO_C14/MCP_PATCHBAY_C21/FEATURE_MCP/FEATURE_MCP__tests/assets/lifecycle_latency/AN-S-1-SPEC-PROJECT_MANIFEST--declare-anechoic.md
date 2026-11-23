---
atom_family: SPEC
atom_id: AN-S-1
container: {component: C00}
tier: -1
context: {template: project_manifest, lens: SPEC}
state: {status: active, version: 1, updated_at: '2026-11-23T00:00:00Z'}
---

## Summary

Anechoic

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN', lens_whitelist=['SPEC'], parameters={'project': {'root': {'prefix': 'underscore'}}, 'runtime': {'journal': {'storage': 'duckdb'}, 'workbench': {'storage': 'memory', 'import_graph': False}}}))
```

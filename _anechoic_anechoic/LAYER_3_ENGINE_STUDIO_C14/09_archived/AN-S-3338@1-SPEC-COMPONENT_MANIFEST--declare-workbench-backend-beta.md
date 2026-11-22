---
atom_family: SPEC
atom_id: AN-S-3338
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T11:41:29.815944+00:00"
---
## Summary

Declare Workbench Backend Beta

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C70',
        name='Workbench Backend Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': {'only': ['C16', 'C53']}}, 'io': {'server': {'project_admission': {'transport': 'json_lines', 'runner': 'managed_python', 'module': 'WORKBENCH_BACKEND_beta_C70.project_admission__pub'}, 'workbench_api': {'transport': 'http', 'socket': 'private Unix socket', 'runner': 'managed_python', 'module': 'WORKBENCH_BACKEND_beta_C70.runtime__pub', 'routes': ['GET /health', 'GET /tools', 'POST /tools', 'GET /jobs/worker-runs']}}, 'client': {'database': {'component': 'C71', 'transport': 'http'}, 'jobs': {'component': 'C68', 'transport': 'http'}, 'reviewed_model': {'transport': 'cli', 'runner': 'managed_python', 'module': 'FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile'}}}, 'state': {'reads': ['Project Manifest', 'reviewed Model', 'Project binding'], 'writes': []}},
    ),
)
```

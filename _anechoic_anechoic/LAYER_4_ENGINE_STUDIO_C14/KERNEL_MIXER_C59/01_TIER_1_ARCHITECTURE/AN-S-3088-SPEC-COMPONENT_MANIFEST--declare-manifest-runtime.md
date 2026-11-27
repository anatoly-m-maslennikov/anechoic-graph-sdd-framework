---
atom_family: SPEC
atom_id: AN-S-3088
container:
  component: C59
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 24
  updated_at: "2026-11-26T15:52:28.186147+00:00"
---

## Summary

Declare Manifest Runtime

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C62',
    name='Manifest Runtime',
    lens_whitelist=['SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['MANIFEST_RUNTIME_C62__shared.run_manifest_runtime',
                      'structure_host_CS3__shared.publish_structure',
                      'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                      'ORCHESTRATOR_C66__shared.Orchestrator',
                      'ADAPTERS_C30__shared.ARCHIVE_DIRECTORY',
                      'ADAPTERS_C30__shared.DRAFT_DIRECTORY',
                      'ADAPTERS_C30__shared.READY_DIRECTORY',
                      'ADAPTERS_C30__shared.owned_temporary_root',
                      'source_watcher__pub.SourceWatcher'],
          'exports': {'MANIFEST_RUNTIME_C62__shared.compile_reviewed_model': {'private': ['CS2']},
                      'MANIFEST_RUNTIME_C62__shared.run_manifest_runtime': {'private': ['C59',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/MANIFEST_RUNTIME_C62/MANIFEST_RUNTIME_C62__tests']}}},
 'io': {'client': [{'component': 'C66', 'interface': 'compiler_worker'}]},
 'state': {'reads': ['pinned Project Manifest and compiler output'],
           'writes': ['admitted Model and Structure generation']}}
```

## Component Contract

### Serve the compiled Model and Structure

#### Guarantee

For a selected native Project, host the admitted Model and validated
Structure in the Kernel process. Provide the compiled Model directory,
bound Model, and Structure snapshot path after verifying that the Model
and initial Structure share one Model source fingerprint.

Run the Manifest Builder in a bounded separate process. On relevant
Manifest changes, validate each replacement Structure against the admitted
Model and publish it atomically. Keep the last accepted Structure if a
rebuild fails. Admit a changed Model on restart.

#### References

AN-S-3088, AN-S-3089, AN-S-3090, AN-S-3091, and AN-T-2947.

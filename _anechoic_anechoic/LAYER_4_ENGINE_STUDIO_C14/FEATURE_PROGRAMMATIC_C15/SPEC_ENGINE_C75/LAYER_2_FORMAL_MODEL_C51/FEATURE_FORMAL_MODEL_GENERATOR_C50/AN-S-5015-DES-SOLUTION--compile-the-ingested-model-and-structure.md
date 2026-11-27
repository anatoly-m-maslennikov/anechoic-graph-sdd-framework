---
atom_family: SPEC
atom_id: AN-S-5015
container:
  component: C50
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3065@39
state:
  status: active
  version: 2
  updated_at: '2026-11-27T11:43:54.041100+00:00'
---

## Summary

Compile the ingested Model and Structure

## Claim

### Prose Claim

Compare the accepted Model's input fingerprint with the current fingerprint, which covers the Model inputs and compiler sources. Reuse it if the fingerprints match, the file loads, and no explicit Model rebuild was requested. On a miss with usable inputs, compile once.

Validate the selected Model with the Structure compiler supplied by C75. If Model or Structure validation fails, record the rejection and try the last usable Model once. Use the bundled reviewed Model when no accepted Model is available. Return the staged descriptor digest, Structure, and diagnostics.

A reused descriptor has the same digest as the accepted descriptor.
Compute the returned digest from the staged file in every success case.
The bootstrap and selected Models have separate roles. Open the selected generation
with C53, then use that same Model with the supplied Structure compiler. Carry
its fingerprint and descriptor digest through opening and return. The
returned Structure carries that fingerprint.

### Formal Claim

```python
component_workflow(
    component='C50',
    action='manifest_compile',
    machine={'id': 'c50_managed_model', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'select', 'expect': {
            'kind': 'trigger', 'target': 'manifest_compile',
            'detail': {'interface': 'manifest_compile', 'action': 'manifest_compile',
                       'entry': 'manifest_compiler_CS1__shared.compile_ingested_cli',
                       'transport': 'in_process'}}}}},
        'select': {'on': {
            'asset_validated': {'to': 'reuse_open', 'expect': {
                'kind': 'effect', 'target': 'C50.compiled_model_asset', 'outcome': 'validated',
                'detail': {'force_rebuild': False}, 'bind': {'selected_model': 'model_sha256', 'selected_descriptor': 'descriptor_sha256'}}},
            'cache_miss': {'to': 'compile', 'expect': {
                'kind': 'effect', 'target': 'C50.compiled_model_asset', 'outcome': 'miss'}},
            'forced_rebuild': {'to': 'compile', 'expect': {
                'kind': 'effect', 'target': 'C50.compiled_model_asset', 'outcome': 'bypassed'}},
            'candidate_rejected': {'to': 'fallback', 'expect': {
                'kind': 'effect', 'target': 'C50.model_diagnostics', 'outcome': 'recorded'}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'compile': {'on': {
            'candidate_staged': {'to': 'compiled_open', 'expect': {
                'kind': 'effect', 'target': 'C50.model_generation', 'outcome': 'staged', 'bind': {'selected_model': 'model_sha256', 'selected_descriptor': 'descriptor_sha256'}}},
            'candidate_rejected': {'to': 'fallback', 'expect': {
                'kind': 'effect', 'target': 'C50.model_diagnostics', 'outcome': 'recorded'}},
        }},
        'reuse_open': {'on': {
            'reuse_model_opened': {'to': 'reuse_structure', 'expect': {
                'kind': 'effect', 'target': 'C53', 'outcome': 'opened', 'detail': {'component': 'C53', 'action': 'open_admitted_model', 'output': 'succeeded', 'manifest': 'AN-S-3067@44', 'interface': 'admitted_model', 'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model', 'transport': 'in_process'}, 'same_as': {'model_sha256': 'selected_model', 'descriptor_sha256': 'selected_descriptor'}}},
            'open_rejected': {'to': 'fallback', 'expect': {'kind': 'effect', 'target': 'C50.model_diagnostics', 'outcome': 'recorded'}},
        }},
        'reuse_structure': {'on': {
            'structure_ready': {'to': 'reused', 'expect': {
                'kind': 'effect', 'target': 'C93.structure_snapshot', 'outcome': 'ready', 'same_as': {'model_sha256': 'selected_model'}}},
            'structure_rejected': {'to': 'fallback', 'expect': {
                'kind': 'effect', 'target': 'C50.model_diagnostics', 'outcome': 'recorded'}},
        }},
        'compiled_open': {'on': {
            'compiled_model_opened': {'to': 'compiled_structure', 'expect': {
                'kind': 'effect', 'target': 'C53', 'outcome': 'opened', 'detail': {'component': 'C53', 'action': 'open_admitted_model', 'output': 'succeeded', 'manifest': 'AN-S-3067@44', 'interface': 'admitted_model', 'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model', 'transport': 'in_process'}, 'same_as': {'model_sha256': 'selected_model', 'descriptor_sha256': 'selected_descriptor'}}},
            'open_rejected': {'to': 'fallback', 'expect': {'kind': 'effect', 'target': 'C50.model_diagnostics', 'outcome': 'recorded'}},
        }},
        'compiled_structure': {'on': {
            'structure_ready': {'to': 'compiled', 'expect': {
                'kind': 'effect', 'target': 'C93.structure_snapshot', 'outcome': 'ready', 'same_as': {'model_sha256': 'selected_model'}}},
            'structure_rejected': {'to': 'fallback', 'expect': {
                'kind': 'effect', 'target': 'C50.model_diagnostics', 'outcome': 'recorded'}},
        }},
        'fallback': {'on': {
            'fallback_selected': {'to': 'fallback_open', 'expect': {
                'kind': 'effect', 'target': 'C50.model_generation', 'outcome': 'restored', 'bind': {'selected_model': 'model_sha256', 'selected_descriptor': 'descriptor_sha256'}}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'fallback_open': {'on': {
            'fallback_model_opened': {'to': 'fallback_structure', 'expect': {
                'kind': 'effect', 'target': 'C53', 'outcome': 'opened', 'detail': {'component': 'C53', 'action': 'open_admitted_model', 'output': 'succeeded', 'manifest': 'AN-S-3067@44', 'interface': 'admitted_model', 'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model', 'transport': 'in_process'}, 'same_as': {'model_sha256': 'selected_model', 'descriptor_sha256': 'selected_descriptor'}}},
            'open_rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'fallback_structure': {'on': {
            'structure_ready': {'to': 'restored', 'expect': {
                'kind': 'effect', 'target': 'C93.structure_snapshot', 'outcome': 'ready', 'same_as': {'model_sha256': 'selected_model'}}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'reused': {'on': {'returned': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'reused', 'same_as': {'model_sha256': 'selected_model', 'model_descriptor_sha256': 'selected_descriptor'}}}}},
        'compiled': {'on': {'returned': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'compiled', 'same_as': {'model_sha256': 'selected_model', 'model_descriptor_sha256': 'selected_descriptor'}}}}},
        'restored': {'on': {'returned': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'fallback', 'same_as': {'model_sha256': 'selected_model', 'model_descriptor_sha256': 'selected_descriptor'}}}}},
        'done': {'type': 'final'},
    }},
)
```

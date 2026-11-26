---
atom_family: SPEC
atom_id: AN-S-3309
container:
  component: C24
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3049
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T09:24:46Z'
---
## Summary

Query the frozen review Entity index

## Claim

### Prose Claim

`exact_name_first` puts every exact Entity name match before the other
matches. Record properties describe the information carried by each
candidate. The property names in this claim identify logical fields.

### Formal Claim

```python cli
declare_cli_contract(
    interface='query_frozen_review_context',
    action='query_frozen_review_entity_index',
    runner='managed_python',
    path='LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/context_builder.py',
    arguments=('--context', '<frozen-index-json>', '--query', '<text>'),
    checks={
        'output_format': {'encoding': 'json', 'record_properties': ('admission_status', 'source_bindings'), 'record_role': 'review_candidate'},
        'guarantees': {'match_fields': ('indexed_body', 'name'), 'priority': 'exact_name_first'},
        'effects': {'query_scope': 'supplied_frozen_context'},
    },
)
```

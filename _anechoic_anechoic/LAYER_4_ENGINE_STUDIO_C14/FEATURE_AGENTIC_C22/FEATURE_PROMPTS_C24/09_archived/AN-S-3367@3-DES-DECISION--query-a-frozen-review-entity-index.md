---
atom_family: SPEC
atom_id: AN-S-3367
container:
  component: C24
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3309@3-draft
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:09:50.987349+00:00"
---

## Summary

Query a frozen review Entity index

## Claim

### Prose Claim

Start the query workflow with nonempty query text.

### Formal Claim

```python
component_workflow(
    component='C24',
    action='query_frozen_review_entity_index',
    machine={
        'id': 'c24_query_frozen_review_entity_index',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'query_requested': {'target': 'searching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'query_frozen_review_context', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/context_builder.py',
                        'arguments': ['--context', '<frozen-index-json>', '--query', '<text>'],
                    }}}},
            }},
            'searching': {'on': {
                'frozen_context_file_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C24', 'outcome': 'succeeded', 'detail': {
                        'read_source': 'context_argument', 'match_fields': ['name', 'indexed_body'],
                        'rank_first': 'exact_name_match',
                    }}}},
            }},
            'responding': {'on': {
                'candidate_records_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {
                        'encoding': 'json', 'record_properties': ['source_bindings', 'admission_status'],
                        'record_role': 'review_candidate',
                    }}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

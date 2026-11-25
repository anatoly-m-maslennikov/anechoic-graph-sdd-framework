---
atom_family: SPEC
atom_id: AN-S-4750
container:
  component: C57
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4749@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Guide subject atom gathering

## Claim

### Prose Claim

The gatherer prompt is located in FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT, not a separate C57 directory. It instructs a read-only handoff and forbids rewriting Atoms or creating or updating Drafts. A work-specific scratchpad under `.anechoic_tmp` is part of the guided handoff.

The prompt requires pinned Current, Active source Atoms for each exact Main Subject, all parent Subjects, relevant dependencies, and applicable model authorities. It requires complete content, revisions and relation provenance, and records missing, stale or ambiguous inputs and affected passages. Parent Drafts supplied by the workflow remain distinct from their Current sources.

It also requires a reconciled quark pool and lookup, target boundary, read-only context and gaps. Scope selection, parsed ancestry, relevance, complete source coverage and quark fidelity remain semantic obligations outside this model.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT/subject_atom_gatherer.prompt.md`.

This workflow models the prompt's guidance. Its effects represent guidance requirements, not gathered values or proof that an agent complied or that a tool call or write occurred.

```python
component_workflow(
    component='C57',
    action='guide_subject_atom_gathering',
    machine={
        'id': 'c57_guide_subject_atom_gathering',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'gathering_requested': {'target': 'sources', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'sources': {'on': {
                'current_source_pinning_required': {'target': 'parents', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.current_sources', 'outcome': 'pinning_required'}}},
            }},
            'parents': {'on': {
                'parent_context_pinning_required': {'target': 'dependencies', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.parent_context', 'outcome': 'pinning_required'}}},
            }},
            'dependencies': {'on': {
                'dependency_context_pinning_required': {'target': 'gaps', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.dependency_context', 'outcome': 'pinning_required'}}},
            }},
            'gaps': {'on': {
                'gap_reporting_required': {'target': 'handoff', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.gaps', 'outcome': 'reporting_required'}}},
            }},
            'handoff': {'on': {
                'read_only_handoff': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'read_only_handoff'}}},
            }},
            'completed': {'type': 'final'},
        },
    },
)
```

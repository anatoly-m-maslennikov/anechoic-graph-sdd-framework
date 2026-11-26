---
atom_family: SPEC
atom_id: AN-S-4749
container:
  component: C57
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3063
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Guide subject atom gathering

## Guarantee

Guide gathering of pinned Current source Atoms, parent and dependency context, and gaps for a Subject-tree rewrite. The guidance requires a read-only handoff and forbids rewriting Atoms or creating or updating Drafts. Scratchpad preparation is permitted.

The handoff must account for missing or ambiguous inputs and affected passages. Completeness and relevance of the gathered material are semantic obligations; the trace does not establish them.

## Claim

### Formal Claim

This trace models required guidance for a successful handoff, not actual agent or tool execution.

```python trace
declare_trace_contract(
    action='guide_subject_atom_gathering',
    output='read_only_handoff',
    must_effect=(('guidance.current_sources', 'pinning_required'),
                 ('guidance.parent_context', 'pinning_required'),
                 ('guidance.dependency_context', 'pinning_required'),
                 ('guidance.gaps', 'reporting_required')),
    forbid_effect=('draft_write', 'atom_rewrite'),
)
```

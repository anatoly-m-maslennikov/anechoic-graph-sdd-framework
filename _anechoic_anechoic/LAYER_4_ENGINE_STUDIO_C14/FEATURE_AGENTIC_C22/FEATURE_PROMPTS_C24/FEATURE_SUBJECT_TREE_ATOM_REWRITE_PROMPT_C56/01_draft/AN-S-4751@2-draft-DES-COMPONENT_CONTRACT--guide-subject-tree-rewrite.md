---
atom_family: SPEC
atom_id: AN-S-4751
container:
  component: C56
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3064
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:49+00:00'
---

## Summary

Guide subject tree rewrite

## Guarantee

Guide an agent to rebuild gathered Subject Atom sets from pinned sources and retain traceability through Drafts.

## Claim

### Prose Claim

The carrier provides guidance to rebuild from pinned sources and retain source-to-Draft mapping. It instructs the operator to verify each Draft before reporting it. These instructions do not perform those actions.

### Formal Claim

```python trace
declare_trace_contract(
    action='subject_tree_atom_rewrite',
    output='verified_draft_reported',
    must_effect=(('rebuild_guidance', 'provided'), ('traceability_guidance', 'provided')),
    forbid_effect=('draft_write', 'state_write'),
)
```

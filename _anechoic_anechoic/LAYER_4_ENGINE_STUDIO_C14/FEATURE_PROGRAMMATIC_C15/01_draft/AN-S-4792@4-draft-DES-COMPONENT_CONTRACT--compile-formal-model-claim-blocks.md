---
atom_family: SPEC
atom_id: AN-S-4792
container:
  component: C15
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3045
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T11:02:11.485674+00:00'
---

## Summary

Compile formal Model Claim blocks

## Guarantee

Read formal Claim fences. Compile Python Model Claims into statements and retain CFEL statements without comments. Other fence languages do not produce Model statements. Report compilation errors to the caller.

## Claim

### Prose Claim

A statement result contains compiled Python or comment-free CFEL.
Unsupported fences return no Model statements. A compilation error
reports a diagnostic and produces no Model statements for that fence.

### Formal Claim

```python trace
declare_trace_contract(
    action='compile_formal_claim',
    output='python_statements_returned',
    must_effect=(
        ('python_model_claim', 'compiled'),
        ('C15.model_statements', 'python'),
    ),
    must_precede=(
        (('python_model_claim', 'compiled'), ('C15.model_statements', 'python')),
    ),
)
```

```python trace
declare_trace_contract(
    action='compile_formal_claim',
    output='cfel_statements_returned',
    must_effect=(
        ('cfel_comments', 'removed'),
        ('C15.model_statements', 'comment_free_cfel'),
    ),
    must_precede=(
        (('cfel_comments', 'removed'), ('C15.model_statements', 'comment_free_cfel')),
    ),
)
```

```python trace
declare_trace_contract(
    action='compile_formal_claim',
    output='compilation_error',
    must_effect=(
        ('C15.compilation_error', 'reported'),
    ),
    forbid_effect=('C15.model_statements',),
)
```

```python trace
declare_trace_contract(
    action='compile_formal_claim',
    output='no_statements',
    forbid_effect=('C15.model_statements',),
)
```

## Details

The claim covers one fence. Exact statement content and diagnostic
format remain open.

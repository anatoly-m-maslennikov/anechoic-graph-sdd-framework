---
atom_family: SPEC
atom_id: AN-S-4742
container:
  component: C30
tier: 0
context:
  template: solution
  lens: SWD
relations:
  ANSWERS:
  - AN-S-3069@67-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Extract the carrier body.

## Claim

### Prose Claim

For `frontmatter_bounds` and `source_body` in `carrier_body__pub.py`,
select the first eligible exact closing delimiter after an exact opening
line. Return its byte bounds and the unchanged body, or an explicit
missing-delimiter outcome. Use only the supplied byte sequence and path. These operations have no
Project state, filesystem, or network effects.

### Formal Claim

Inputs are byte lists (each integer is between 0 and 255). The outcome abstracts
`source_body`'s path-bearing unsupported-delimiter error. The caller provides the path for the error message.

```python framing
declare_framing_solution(
    opening_prefixes=[[45, 45, 45, 10], [45, 45, 45, 13, 10]],
    closing_prefixes=[
        [13, 10, 45, 45, 45, 13, 10],
        [13, 10, 45, 45, 45, 10],
        [10, 45, 45, 45, 13, 10],
        [10, 45, 45, 45, 10],
    ],
)
```

## Details

The framing model describes results for byte sequences. The Python
implementation must also satisfy the scoped effect guarantees.

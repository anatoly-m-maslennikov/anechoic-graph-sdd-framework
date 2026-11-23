---
atom_family: SPEC
atom_id: AN-S-4421
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 12:02:33 +0400
---
## Summary
Render untrusted Project content only as data

## Claim

### Prose Claim

GRAPH_UI **must** render untrusted Project content as inspectable data **without** executing that content **or** granting it additional capabilities.

the boundary applies **in** **every** supported output context, including text, markup, links, styles, **and** control characters. displaying a value **must not** let that value escape its context **or** become executable authority. The choice of safe rendering technique remains Method-owned.

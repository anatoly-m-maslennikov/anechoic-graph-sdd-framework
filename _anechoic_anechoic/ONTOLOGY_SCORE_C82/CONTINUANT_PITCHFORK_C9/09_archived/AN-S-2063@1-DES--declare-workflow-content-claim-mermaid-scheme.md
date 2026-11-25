---
atom_family: SPEC
atom_id: AN-S-2063
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 21:06:57 +0400
---

## Summary

Declare Workflow.Content.Claim.Mermaid Scheme

## Claim

### Prose Claim

The scheme shows all Workflow Steps, including nested Steps.

### Formal Claim

```CFEL
# model
Workflow.Content.Claim.Mermaid Scheme{::1} :: [markdown]{::1};

Workflow.Content.Claim.Mermaid Scheme.*[]{::0}
```

## Semantics

The value is exactly one `mermaid`-labelled fenced Markdown block. A Mermaid Scheme is a visual Minto summary of its owning Claim's text: removing it must leave that text's specification complete and unchanged. It may repeat the text.

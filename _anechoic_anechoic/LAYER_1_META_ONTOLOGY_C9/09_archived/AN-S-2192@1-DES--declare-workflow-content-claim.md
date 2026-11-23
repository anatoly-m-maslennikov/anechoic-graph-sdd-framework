---
atom_family: SPEC
atom_id: AN-S-2192
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

Declare Workflow.Content.Claim

## Claim

### Formal Claim

```CFEL
# model
Workflow.Content.Claim{::1} :: []{::0};

Workflow.Content.Claim.*[in (Mermaid Scheme, Prose Claim, Formal Claim)]{::1..3};

Workflow.Content.Claim.Mermaid Scheme ;> Workflow.Content.Claim.Prose Claim;

Workflow.Content.Claim.Prose Claim ;> Workflow.Content.Claim.Formal Claim
```

## Semantics

Workflow Claim has unique child Property names. At least one of Prose Claim and Formal Claim is present, and their text together specifies the Workflow completely without reliance on the Mermaid Scheme.

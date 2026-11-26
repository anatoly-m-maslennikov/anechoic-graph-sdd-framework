---
atom_family: SPEC
atom_id: AN-S-2067
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 21:46:20 +0400
---

## Summary

Declare Step.Content.Claim.Mermaid Scheme

## Claim

### Prose Claim

Mermaid Scheme semantics: [Workflow Mermaid Scheme declaration](CA-R-2962-CORE_META_MODEL-DECLARATION--declare-workflow-content-claim-mermaid-scheme.md#semantics).

### Formal Claim

```CFEL
# model
Step.Content.Claim.Mermaid Scheme{::0..1} :: [markdown]{::1};

Step.Content.Claim.Mermaid Scheme.*[]{::0}
```

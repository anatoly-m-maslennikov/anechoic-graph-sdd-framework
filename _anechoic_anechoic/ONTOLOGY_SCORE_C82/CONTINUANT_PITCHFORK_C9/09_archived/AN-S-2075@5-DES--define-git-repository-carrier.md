---
atom_family: SPEC
atom_id: AN-S-2075
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-29 11:35:34 +0400
---
## Summary

Define Git Repository Carrier

## Claim

A Git Repository **means** a Carrier of versioned content and Git references.

### Formal claim

```text
Git Repository > @(Git Branch)
```

## Semantics

A remote repository or branch on GitHub is another Carrier. Git Repository > Git Branch denotes whole/part containment. Local connection names and URLs describe how the repository is selected.

---
atom_family: SPEC
atom_id: AN-S-3496
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Isolate non-git, multi-project and relocated targets

# Summary

Isolate non-git, multi-project and relocated targets

## Scope

the supported target topology variations for one installation contribution.

## Claim

the INSTALL_TOOLS facade **must** distinguish a non-git Project, two Projects in one repository and relocation by separate target contexts, and **must not** use repository root or absolute checkout path as the sole Project identity.

## Details

A non-git context records no repository identity; sibling Projects in one repository require distinct Project identities and control children. Relocation makes a new context with an explicit predecessor and verifies the declared Project identity and controls again. Each target owns separate lock, selector and state; ambiguous topology refuses.
